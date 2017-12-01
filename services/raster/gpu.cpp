#include <iostream>
#include <stdio.h>
#include <math.h>
#include "gpu.h"


#define _mm_movemask_ps( m ) _mm_movemask_ps( ( __m128 )m )


//
union Registers
{
    struct
    {
        __m128_union* IR; // input registers
        __m128_union* OR; // output registers
        __m128_union* CR; // constant registers
        __m128_union* GPR; // general purpose registers
        Image* const * TR; // texture registers
    };
    __m128_union* regs[ REGISTER_TYPES_NUM ];
};


//
inline
void LoadRegister( __m128_union& output, const Registers& registers, u32 regType, u32 regIdx, Swizzle regSwizzle ) {
    output.m128_f32[ 0 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i0 ];
    output.m128_f32[ 1 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i1 ];
    output.m128_f32[ 2 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i2 ];
    output.m128_f32[ 3 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i3 ];
}


inline
void StoreRegister( const Registers& registers, u32 regType, u32 regIdx, Swizzle regSwizzle, const __m128_union& input ) {
    __m128_union& dst = registers.regs[ regType ][ regIdx ];
    if( regSwizzle.activeNum >= 1 )
        dst.m128_f32[ regSwizzle.i0 ] = input.m128_f32[ 0 ];
    if( regSwizzle.activeNum >= 2 )
        dst.m128_f32[ regSwizzle.i1 ] = input.m128_f32[ 1 ];
    if( regSwizzle.activeNum >= 3 )
        dst.m128_f32[ regSwizzle.i2 ] = input.m128_f32[ 2 ];
    if( regSwizzle.activeNum >= 4 )
        dst.m128_f32[ regSwizzle.i3 ] = input.m128_f32[ 3 ];
}


//
bool Execute( const Registers& registers, const Shader& shader ) {
    const i32 MAX_ITERATIONS_NUM = 1024;
    u32 cmpMask = 0;
    for( i32 ip = 0, iter = 0; ip < ( i32 )shader.header.instructionsNum; ip++ ) {
        if( iter >= MAX_ITERATIONS_NUM ) {
            printf( "Execution break: infinite loop detected\n" );
            return false;
        }
        iter++;

        Instruction& i = shader.instructions[ ip ];
		if( i.op < 0 || i.op >= OP_COUNT ) {
			printf( "Execution break: Invalid instruction op code\n" );
			return false;
		}
		
		__m128_union src0, src1, result;

        if( g_opOperands[ i.op ] & OPERAND_SRC0 )
            LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
        if( g_opOperands[ i.op ] & OPERAND_SRC1 )
            LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );

        switch( i.op )
        {
            case OP_INVALID:
                printf( "Execution break: invalid op\n" );
                return false;
                break;
            case OP_SET:
            case OP_SETI:
                {
                    SetInstruction seti = *( SetInstruction* )&i;
                    result.f = _mm_set_ps( seti.floats[ 3 ], seti.floats[ 2 ], seti.floats[ 1 ], seti.floats[ 0 ] );
                }
                break;
            case OP_TFETCH:
                {
                    TFetchInstruction tfetch = *( TFetchInstruction* )&i;
                    Image* texture = registers.TR[ tfetch.textureReg ];
                    if( !texture ) { // unbound texture
                        result.i = _mm_set1_epi32( 0 );
                    } else {
                        __m128_union textureSize, texelPos;
                        textureSize.f = _mm_cvtepi32_ps( _mm_set_epi32( 0, 0, texture->height, texture->width ) );
                        texelPos.i = _mm_cvttps_epi32( _mm_sub_ps( _mm_mul_ps( src0.f, textureSize.f ), _mm_set1_ps( 0.5f ) ) );
                        // wrap sampling mode
                        int x = texelPos.m128_i32[ 0 ] % texture->width;
                        int y = texelPos.m128_i32[ 1 ] % texture->height;
                        RGBA& rgba = texture->rgba[ y * texture->width + x ];
                        result.i = _mm_set_epi32( rgba.a, rgba.b, rgba.g, rgba.r );
                    }
                }
                break;
            case OP_ADD:  result.f = _mm_add_ps   ( src0.f, src1.f ); break;
            case OP_ADDI: result.i = _mm_add_epi32( src0.i, src1.i ); break;
            case OP_SUB:  result.f = _mm_sub_ps   ( src0.f, src1.f ); break;
            case OP_SUBI: result.i = _mm_sub_epi32( src0.i, src1.i ); break;
            case OP_MUL:  result.f = _mm_mul_ps   ( src0.f, src1.f ); break;
            case OP_MULI:
                {
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        result.m128_i32[ j ] = src0.m128_i32[ j ] * src1.m128_i32[ j ];
                }
                break;
            case OP_DIV:  result.f = _mm_div_ps   ( src0.f, src1.f ); break;
            case OP_DIVI:
                {
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ ) {
						if( src1.m128_i32[ j ] == 0 ) {
							printf( "Execution break: integer division by zero\n" );
            				return false;
						}
                        result.m128_i32[ j ] = src0.m128_i32[ j ] / src1.m128_i32[ j ];
					}
                }
                break;
            case OP_DOT:
                {
#if DEBUG
                    if( i.src0Swizzle.activeNum != i.src1Swizzle.activeNum ) {
                        printf( "i.src0Swizzle.activeNum != i.src1Swizzle.activeNum\n" );
                        return false;
                    }
#endif
                    __m128_union tmp;
                    tmp.f = _mm_mul_ps( src0, src1 );
                    f32 dot = 0.0f;
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        dot += tmp.m128_f32[ j ];
                    result.f = _mm_set_ps1( dot );
                }
                break;
            case OP_LENGTH:
                {
                    __m128_union tmp;
                    tmp.f = _mm_mul_ps( src0.f, src0.f );
                    f32 dot = 0.0f;
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        dot += tmp.m128_f32[ j ];
                    result.f = _mm_set1_ps( sqrt( dot ) );
                }
                break;
            case OP_NORMALIZE:
                {
                    __m128_union tmp;
                    tmp.f = _mm_mul_ps( src0.f, src0.f );
                    f32 dot = 0.0f;
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        dot += tmp.m128_f32[ j ];
                    f32 length = sqrt( dot );
                    tmp.f = _mm_set1_ps( length );
                    result.f = _mm_div_ps( src0.f, tmp.f );
                }
                break;
            case OP_ABS:
                {
                    __m128_union tmp;
                    tmp.f = _mm_set1_ps( -0.0f );
                    result.f = _mm_andnot_ps( tmp.f, src0.f );
                }
                break;
            case OP_SATURATE:
                {
                    __m128_union min, max;
                    min.f = _mm_set1_ps( 0.0f );
                    max.f = _mm_set1_ps( 1.0f );
                    result.f = _mm_max_ps( src0.f, min );
                    result.f = _mm_min_ps( result.f, max );
                }
                break;
            case OP_MOV:   result = src0; break;
            case OP_CVTFI: result.i = _mm_cvttps_epi32( src0 ); break;
            case OP_CVTIF: result.f = _mm_cvtepi32_ps( src0.i ); break;
            case OP_CMPEQ: cmpMask = _mm_movemask_ps( _mm_cmpeq_ps   ( src0.f, src1.f ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPLT: cmpMask = _mm_movemask_ps( _mm_cmplt_ps   ( src0.f, src1.f ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPLE: cmpMask = _mm_movemask_ps( _mm_cmple_ps   ( src0.f, src1.f ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPGT: cmpMask = _mm_movemask_ps( _mm_cmpgt_ps   ( src0.f, src1.f ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPGE: cmpMask = _mm_movemask_ps( _mm_cmpge_ps   ( src0.f, src1.f ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPEQI:cmpMask = _mm_movemask_ps( _mm_cmpeq_epi32( src0.i, src1.i ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPLTI:cmpMask = _mm_movemask_ps( _mm_cmplt_epi32( src0.i, src1.i ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_CMPGTI:cmpMask = _mm_movemask_ps( _mm_cmpgt_epi32( src0.i, src1.i ) ) & ( ( 1 << i.src0Swizzle.activeNum ) - 1 ); break;
            case OP_JMP_TRUE:
                if( cmpMask ) {
                    JumpInstruction jmp = *( JumpInstruction* )&i;
                    ip += jmp.offset;
                    ip -= 1;
                    if( ip < -1 ) {
                        printf( "Invalid jump, force exit\n" );
                        return false;
                    }
                }
                break;
            case OP_JMP_FALSE:
                if( !cmpMask ) {
                    JumpInstruction jmp = *( JumpInstruction* )&i;
                    ip += jmp.offset;
                    ip -= 1;
                    if( ip < -1 ) {
                        printf( "Invalid jump, force exit\n" );
                        return false;
                    }
                }
                break;
            case OP_OR: result.f = _mm_or_ps( src0.f, src1.f ); break;
            case OP_AND: result.f = _mm_and_ps( src0.f, src1.f ); break;
            case OP_XOR: result.f = _mm_xor_ps( src0.f, src1.f ); break;
            case OP_SHL:
                {
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        result.m128_i32[ j ] = src0.m128_i32[ j ] << src1.m128_i32[ j ];
                }
                break;
            case OP_SHR:
                {
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        result.m128_i32[ j ] = src0.m128_i32[ j ] >> src1.m128_i32[ j ];
                }
                break;
            case OP_RET: return true;
        }

        if( g_opOperands[ i.op ] & OPERAND_DST )
            StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
    }
    return true;
}


//
struct Point2D {
    i32 x, y;
};


//
i32 EdgeFunction( const Point2D& a, const Point2D& b, const Point2D& c ) {
    return ( b.x - a.x ) * ( c.y - a.y ) - ( b.y - a.y ) * ( c.x - a.x );
}


//
__m128 Interpolate( f32 l0, f32 l1, f32 l2, const __m128_union& v0, const __m128_union& v1, const __m128_union& v2 ){
    __m128 m0 = _mm_mul_ps( v0.f, _mm_set1_ps( l0 ) );
    __m128 m1 = _mm_mul_ps( v1.f, _mm_set1_ps( l1 ) );
    __m128 m2 = _mm_mul_ps( v2.f, _mm_set1_ps( l2 ) );
    __m128 ret = _mm_add_ps( m0, _mm_add_ps( m1, m2 ) );
    return ret;
}


//
void Draw( const PipelineState& pState ) {
    const u32 VARYINGS_PER_VERTEX = 4;
    if( pState.vs->header.type != SHADER_VERTEX )
        return;
    if( pState.ps->header.type != SHADER_PIXEL )
        return;
    if( pState.vs->header.vs.varyingsNum > VARYINGS_PER_VERTEX )
        return;
	
	// viewport scale and offset
    __m128 vpScale  = _mm_set_ps( 1.0f, 1.0f, -0.5f * pState.rt->height, 0.5f * pState.rt->width );
    __m128 vpOffset = _mm_set_ps( 0.0f, 0.0f,  0.5f * pState.rt->height, 0.5f * pState.rt->width );

    __m128_union GPR[ 256 ];
    // 4 varyings for each vertex of triangle
    __m128_union varyings[ VARYINGS_PER_VERTEX * 3 ];

    u32 varyingsNum = std::max( ( u32 )pState.vs->header.vs.varyingsNum, 1u );

    __m128 ones = _mm_set1_ps( 1.0f );

    u32 indicesNum = pState.ib ? pState.ib->indicesNum : pState.vb->vertexNum;
    for( u32 t = 0; t < indicesNum / 3; t++ ) {
        // vertex shader stage
        u32* indices = nullptr;
        u32 autoIndexBuffer[ 3 ];
        if( pState.ib )
            indices = &pState.ib->indices[ t * 3 ];
        else {
            autoIndexBuffer[ 0 ] = t * 3 + 0;
            autoIndexBuffer[ 1 ] = t * 3 + 1;
            autoIndexBuffer[ 2 ] = t * 3 + 2;
            indices = autoIndexBuffer;
        }
        i16 minX = 32767;
        i16 minY = 32767;
        i16 maxX = 0;
        i16 maxY = 0;
        Point2D v[ 3 ];
        bool skipTriangle = false;
        for( u32 vi = 0; vi < 3; vi++ )
        {
            Registers vsRegs;
            u32& index = indices[ vi ];
            vsRegs.IR = &pState.vb->vertices[ index * pState.vb->vertexComponents ];
            vsRegs.OR = &varyings[ VARYINGS_PER_VERTEX * vi ];
            vsRegs.CR = const_cast< __m128_union* >( &pState.constants[ 0 ] );
            vsRegs.GPR = GPR;
            vsRegs.TR = pState.textures;
            if( !Execute( vsRegs, *pState.vs ) )
				return;

            // o0 is always position, so perform perspective divide on it
            __m128_union& pos = vsRegs.OR[ 0 ];
            __m128_union invW;
            invW.f = _mm_shuffle_ps( pos, pos, 0xFF );
            invW.f = _mm_div_ps( ones, invW.f );
            pos.f = _mm_mul_ps( pos, invW.f );

            // near and far planes clip
            if( pos.m128_f32[ 2 ] > 1.0f || pos.m128_f32[ 2 ] < 0.0f ) {
                skipTriangle = true;
                break;
            }

            pos.m128_f32[ 3 ] = invW.m128_f32[ 3 ];
            // ...and ndc to screen space conversion
			pos.f = _mm_add_ps( _mm_mul_ps( pos, vpScale ), vpOffset );
            v[ vi ].x = pos.m128_f32[ 0 ] + 0.5f;
            v[ vi ].y = pos.m128_f32[ 1 ] + 0.5f;
            // tri bounds
            if( v[ vi ].x > maxX ) maxX = v[ vi ].x;
            if( v[ vi ].y > maxY ) maxY = v[ vi ].y;
            if( v[ vi ].x < minX ) minX = v[ vi ].x;
            if( v[ vi ].y < minY ) minY = v[ vi ].y;

            // enable perspective correct interpolation
            for( u32 i = 1; i < varyingsNum; i++ )
                vsRegs.OR[ i ].f = _mm_mul_ps( vsRegs.OR[ i ].f, invW );
        }

        // clip againts screen
        minX = std::max( minX, i16( 0 ) );
        minY = std::max( minY, i16( 0 ) );
        maxX = std::min( maxX, i16( pState.rt->width - 1 ) );
        maxY = std::min( maxY, i16( pState.rt->height - 1 ) );

        // fixed function stage
        int doubleTriArea = EdgeFunction( v[ 0 ], v[ 1 ], v[ 2 ] );
        if( doubleTriArea <= 0 || skipTriangle )
            continue;
        f32 invDoubleArea = 1.0f / ( f32 )doubleTriArea;

        // pixel shader stage
        Point2D p;
        for( p.y = minY; p.y <= maxY; p.y++ ){
            for( p.x = minX; p.x <= maxX; p.x++ ){
                i32 w0 = EdgeFunction( v[ 1 ], v[ 2 ], p );
                i32 w1 = EdgeFunction( v[ 2 ], v[ 0 ], p );
                i32 w2 = EdgeFunction( v[ 0 ], v[ 1 ], p );

                // If p is on or inside all edges, run pixel shader.
                if( ( w0 | w1 | w2 ) >= 0 ) {
                    f32 l0 = ( f32 )w0 * invDoubleArea;
                    f32 l1 = ( f32 )w1 * invDoubleArea;
                    f32 l2 = ( f32 )w2 * invDoubleArea;

                     __m128_union input[ VARYINGS_PER_VERTEX ];
                    input[ 0 ].f = Interpolate( l0, l1, l2,
                                                varyings[ VARYINGS_PER_VERTEX * 0 ],
                                                varyings[ VARYINGS_PER_VERTEX * 1 ],
                                                varyings[ VARYINGS_PER_VERTEX * 2 ] );
                    f32 oneOverZ = input[ 0 ].m128_f32[ 3 ];
                    f32 Z = 1.0f / oneOverZ;
                    __m128 zVec = _mm_set1_ps( Z );

                    for( u32 i = 1; i < varyingsNum; i++ ){
                        input[ i ].f = Interpolate( l0, l1, l2,
                                                    varyings[ VARYINGS_PER_VERTEX * 0 + i ],
                                                    varyings[ VARYINGS_PER_VERTEX * 1 + i ],
                                                    varyings[ VARYINGS_PER_VERTEX * 2 + i ] );
                        input[ i ].f = _mm_mul_ps( input[ i ].f, zVec );
                    }

                    // depth test
                    if( pState.depthRt ) {
                        float& depth = pState.depthRt->f32[ p.y * pState.depthRt->width + p.x ];
                        if( input[ 0 ].m128_f32[ 2 ] > depth )
                            continue;
                        depth = input[ 0 ].m128_f32[ 2 ];
                    }

                    __m128_union output;
                    Registers psRegs;
                    psRegs.IR = input;
                    psRegs.OR = &output;
                    psRegs.CR = const_cast< __m128_union* >( &pState.constants[ 0 ] );
                    psRegs.GPR = GPR;
                    psRegs.TR = pState.textures;
                    if( !Execute( psRegs, *pState.ps ) )
						return;

                    RGBA& rgba = pState.rt->rgba[ p.y * pState.rt->width + p.x ];
					rgba.r = output.m128_u32[ 0 ];
					rgba.g = output.m128_u32[ 1 ];
					rgba.b = output.m128_u32[ 2 ];
                    rgba.a = output.m128_u32[ 3 ];
                }
            }
        }
    }
}


//
void ClearRenderTarget( Image* rt, u8 r, u8 g, u8 b, u8 a ) {
    if( !rt )
        return;

    RGBA rgba;
    rgba.r = r;
    rgba.g = g;
    rgba.b = b;
    rgba.a = a;

    __m128i vec = _mm_set1_epi32( rgba.rgba );
    u32 size = rt->width * rt->height;
    for( u32 i = 0; i < size; i += 4 ) {
        __m128i* dst = ( __m128i* )&rt->rgba[ i ];
        *dst = vec;
    }
}


//
void ClearDepthRenderTarget( Image* depthRt, float value ) {
    if( !depthRt )
        return;

    __m128 vec = _mm_set1_ps( value );
    u32 size = depthRt->width * depthRt->height;
    for( u32 i = 0; i < size; i += 4 ) {
        __m128* dst = ( __m128* )&depthRt->f32[ i ];
        *dst = vec;
    }
}
