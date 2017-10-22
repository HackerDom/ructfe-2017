#include <iostream>
#include <malloc.h>
#include "types.h"
#include "png.h"


//
struct Shader
{
    Instruction* instructions;
    u32 instructionsNum;
};


//
struct VertexBuffer
{
    u32 vertexNum;
    u32 vertexComponents;
    __m128_union* vb;

    VertexBuffer()
        : vertexNum( 0 ), vertexComponents( 0 ), vb( nullptr )
    {}

    VertexBuffer( u32 vertexNum, u32 vertexComponents ) {
        this->vertexNum = vertexNum;
        this->vertexComponents = vertexComponents;
        vb = ( __m128_union* )memalign( 16, vertexNum * vertexComponents * sizeof( __m128 ) );
    }

    ~VertexBuffer() {
        if( !vb )
            free( vb );
    }
};


//
struct RenderTarget
{
    i16 width;
    i16 height;
    u32* pixels;
};


//
struct Registers
{
    union
    {
        struct
        {
            __m128_union* IR; // input registers
            __m128_union* OR; // output registers
            __m128_union* CR; // constant registers
            __m128_union* GPR; // general purpose registers
        };
        __m128_union* regs[ REGISTER_TYPES_NUM ];
    };
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

    for( u32 ip = 0; ip < shader.instructionsNum; ip++ )
    {
        Instruction& i = shader.instructions[ ip ];

        __m128_union src0, src1, result;
        switch( i.op )
        {
            case OP_INVALID:
#if DEBUG
                printf( "Invalid op\n" );
#endif
                return false;
            case OP_SET:
                {
                    f32* floats = ( ( f32* )&i ) + 3; // skip op and dst
                    result.f = _mm_set_ps( floats[ 3 ], floats[ 2 ], floats[ 1 ], floats[ 0 ] );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
                }
                break;
            case OP_ADD:
                {
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );
                    result.f = _mm_add_ps( src0, src1 );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
                }
                break;
            case OP_SUB:
                {
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );
                    result.f = _mm_sub_ps( src0, src1 );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
                }
                break;
            case OP_MUL:
                {
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );
                    result.f = _mm_mul_ps( src0, src1 );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
                }
                break;
            case OP_DIV:
                {
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );
                    result.f = _mm_div_ps( src0, src1 );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
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
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    LoadRegister( src1, registers, i.src1Type, i.src1, i.src1Swizzle );
                    __m128_union tmp;
                    tmp.f = _mm_mul_ps( src0, src1 );
                    f32 dot = 0.0f;
                    for( u32 j = 0; j < i.src0Swizzle.activeNum; j++ )
                        dot += tmp.m128_f32[ j ];
                    result.f = _mm_set_ps1( dot );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, result );
                }
                break;
            case OP_MOV:
                {
                    LoadRegister( src0, registers, i.src0Type, i.src0, i.src0Swizzle );
                    StoreRegister( registers, i.dstType, i.dst, i.dstSwizzle, src0 );
                }
                break;
            case OP_RET:
                return true;
        }
    }

    return true;
}


//
struct Point2D {
    i32 x, y;
};


//
i32 orient2d(const Point2D& a, const Point2D& b, const Point2D& c)
{
    return (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x);
}


//
__m128 Interpolate( int w0, int w1, int w2, float invDoubleArea, const __m128_union& v0, const __m128_union& v1, const __m128_union& v2 ){
    float l0 = w0 * invDoubleArea;
    float l1 = w1 * invDoubleArea;
    float l2 = w2 * invDoubleArea;

    __m128 m0 = _mm_mul_ps( v0.f, _mm_set1_ps( l0 ) );
    __m128 m1 = _mm_mul_ps( v1.f, _mm_set1_ps( l1 ) );
    __m128 m2 = _mm_mul_ps( v2.f, _mm_set1_ps( l2 ) );
    __m128 ret = _mm_add_ps( m0, _mm_add_ps( m1, m2 ) );
    return ret;
}


//
void Draw(  __m128_union* constants, const Shader& vs, const VertexBuffer& vb, const Shader& ps, const Image& rt )
{
    __m128_union* GPR = ( __m128_union* )memalign( 16, 256 * sizeof( __m128 ) );
    const u32 VARYINGS_PER_VERTEX = 4;
    // 4 varyings for each vertex of triangle
    __m128_union varyings[ VARYINGS_PER_VERTEX * 3 ];

    for( u32 t = 0; t < vb.vertexNum / 3; t++ )
    {
        // vertex shader stage
        __m128_union* vsInput = &vb.vb[ 3 * vb.vertexComponents * t ];
        i16 minX = 255;
        i16 minY = 255;
        i16 maxX = 0;
        i16 maxY = 0;
        i16 X[ 3 ], Y[ 3 ];
        f32 Z[ 3 ];
        //f32 W[ 3 ];
        for( u32 v = 0; v < 3; v++ )
        {
            Registers vsRegs;
            vsRegs.IR = &vsInput[ v * vb.vertexComponents ];
            vsRegs.OR = &varyings[ VARYINGS_PER_VERTEX * v ];
            vsRegs.CR = constants;
            vsRegs.GPR = GPR;
            Execute( vsRegs, vs );

            // o0 is always position, so perform perspective divide on it
            __m128_union pos = vsRegs.OR[ 0 ];
            __m128_union w;
            w.f = _mm_shuffle_ps( pos, pos, 0xFF );
            pos.f = _mm_div_ps( pos, w );
            // ...and ndc to screen space conversion
            __m128_union tmp;
            tmp.f = _mm_mul_ps( pos, _mm_set_ps( 1.0f, 1.0f, -0.5f, 0.5f ) );
            tmp.f = _mm_add_ps( tmp, _mm_set_ps( 0.0f, 0.0f, 0.5f, 0.5f ) ); //0.5f, 0.5f, 0.0f, 0.0f ) );
            pos.f = _mm_mul_ps( tmp, _mm_set_ps( 1.0f, 1.0f, rt.height, rt.width ) );
            X[ v ] = pos.m128_f32[ 0 ] + 0.5f;
            Y[ v ] = pos.m128_f32[ 1 ] + 0.5f;
            Z[ v ] = pos.m128_f32[ 2 ];
            // tri bounds
            if( X[ v ] > maxX ) maxX = X[ v ];
            if( Y[ v ] > maxY ) maxY = Y[ v ];
            if( X[ v ] < minX ) minX = X[ v ];
            if( Y[ v ] < minY ) minY = Y[ v ];
        }

        // clip againts screen
        minX = std::max( minX, i16( 0 ) );
        minY = std::max( minY, i16( 0 ) );
        maxX = std::min( maxX, i16( rt.width - 1 ) );
        maxY = std::min( maxY, i16( rt.height - 1 ) );

        // fixed function stage
        int doubleTriArea = (X[1] - X[0]) * (Y[2] - Y[0]) - (X[0] - X[2]) * (Y[0] - Y[1]);
        if( doubleTriArea <= 0 )
            continue;
        f32 invDoubleArea = 1.0f / ( f32 )doubleTriArea;

        Point2D p;
        Point2D v0 = { X[ 0 ], Y[ 0 ] };
        Point2D v1 = { X[ 1 ], Y[ 1 ] };
        Point2D v2 = { X[ 2 ], Y[ 2 ] };
        for( p.y = minY; p.y <= maxY; p.y++ ){
            for( p.x = minX; p.x <= maxX; p.x++ ){
                int w0 = orient2d(v1, v2, p);
                int w1 = orient2d(v2, v0, p);
                int w2 = orient2d(v0, v1, p);

                // If p is on or inside all edges, run pixel shader.
                if( ( w0 | w1 | w2 ) >= 0 ) {
                    //rt.rgba[ p.y * rt.width + p.x ].rgba = ~0u;
                    __m128_union input[ VARYINGS_PER_VERTEX ];
                    for( u32 i = 0; i < VARYINGS_PER_VERTEX; i++ ){
                        input[ i ].f = Interpolate( w0, w1, w2, invDoubleArea,
                                                    varyings[ VARYINGS_PER_VERTEX * 0 + i ],
                                                    varyings[ VARYINGS_PER_VERTEX * 1 + i ],
                                                    varyings[ VARYINGS_PER_VERTEX * 2 + i ]
                                                    );
                    }

                    __m128_union output;
                    Registers psRegs;
                    psRegs.IR = input;
                    psRegs.OR = &output;
                    psRegs.CR = constants;
                    psRegs.GPR = GPR;
                    Execute( psRegs, ps );

                    RGBA& rgba = rt.rgba[ p.y * rt.width + p.x ];
                    rgba.r = output.m128_f32[ 0 ] * 255.0f;
                    rgba.g = output.m128_f32[ 1 ] * 255.0f;
                    rgba.b = output.m128_f32[ 2 ] * 255.0f;
                    rgba.a = output.m128_f32[ 3 ] * 255.0f;
                }
            }
        }
    }

    free( GPR );
}

void DrawTest()
{
    Image image( 32, 32 );
    Instruction vsInsts[ 8 ];
    Instruction* vsPtr = &vsInsts[ 0 ];

    vsPtr->op = OP_MOV;
    vsPtr->dst = 0;
    vsPtr->dstType = REGISTER_OR;
    vsPtr->dstSwizzle.swizzle = 0b11100100;
    vsPtr->dstSwizzle.activeNum = 4;
    vsPtr->src0 = 0;
    vsPtr->src0Type = REGISTER_IR;
    vsPtr->src0Swizzle.swizzle = 0b11100100;
    vsPtr++;

    vsPtr->op = OP_MOV;
    vsPtr->dst = 1;
    vsPtr->dstType = REGISTER_OR;
    vsPtr->dstSwizzle.swizzle = 0b11100100;
    vsPtr->dstSwizzle.activeNum = 4;
    vsPtr->src0 = 1;
    vsPtr->src0Type = REGISTER_IR;
    vsPtr->src0Swizzle.swizzle = 0b11100100;
    vsPtr++;

    vsPtr->op = OP_RET;
    vsPtr->dst = 0;
    vsPtr->dstType = REGISTER_GPR;
    vsPtr->src0 = 0;
    vsPtr->src0Type = REGISTER_GPR;
    vsPtr->src1 = 0;
    vsPtr->src1Type = REGISTER_GPR;

    Shader vs;
    vs.instructions = &vsInsts[ 0 ];
    vs.instructionsNum = 2;

    VertexBuffer vb( 3, 2 );
    vb.vb[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  0.0f );
    vb.vb[ 0 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f,  0.0f,  1.0f );

    vb.vb[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f, -1.0f );
    vb.vb[ 1 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  0.0f );

    vb.vb[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  1.0f );
    vb.vb[ 2 * 2 + 1 ].f = _mm_set_ps( 1.0f, 1.0f,  0.0f,  0.0f );

    Instruction psInsts[ 8 ];
    Instruction* psPtr = &psInsts[ 0 ];

    psPtr->op = OP_MOV;
    psPtr->dst = 0;
    psPtr->dstType = REGISTER_OR;
    psPtr->dstSwizzle.swizzle = 0b11100100;
    psPtr->dstSwizzle.activeNum = 4;
    psPtr->src0 = 1;
    psPtr->src0Type = REGISTER_IR;
    psPtr->src0Swizzle.swizzle = 0b11100100;
    psPtr++;

    psPtr->op = OP_RET;
    psPtr->dst = 0;
    psPtr->dstType = REGISTER_GPR;
    psPtr->src0 = 0;
    psPtr->src0Type = REGISTER_GPR;
    psPtr->src1 = 0;
    psPtr->src1Type = REGISTER_GPR;

    Shader ps;
    ps.instructions = &psInsts[ 0 ];
    ps.instructionsNum = 2;

    Draw( nullptr, vs, vb, ps, image );
    save_png( "test.png", image );
}

int main()
{
    DrawTest();
    Registers registers;
    registers.IR =  ( __m128_union* )memalign( 16, 256 * sizeof( __m128 ) );
    registers.OR =  ( __m128_union* )memalign( 16, 256 * sizeof( __m128 ) );
    registers.GPR = ( __m128_union* )memalign( 16, 256 * sizeof( __m128 ) );

    // iX - IR
    // oX - OR
    // cX - CR
    // rX - GPR
    //add r0.xyzw r1.xyzw r2.xyzw
    //add r0.x r1.x r2.y  		: add dst.x src0.xyzw src1.yyzw
    //add r0.yx r1.xw r2.zy     : add dst.yx src0.xwzw src1.zyzw ( 1, 4 ) + ( 30, 20 ) = ( x, x, 31, 24 )
    //add r0.wy r1.xw r2.zy     : add dst.yx src0.xwzw src1.zyzw ( 1, 4 ) + ( 30, 20 ) = ( 31, x, 24, x )
    //dot r0.x r1.xy r2.zw     1 * 30 + 2 * 40 = 30 + 80 = 110
    //dot r0.xy r1.xyz r2.zwz  1 * 30 + 2 * 40 + 3 * 30 = 110 + 90 = 200

    //registers.GPR[ 0 ].f =  _mm_set_ps1( 0 );
    //registers.GPR[ 1 ].f =  _mm_set_ps( 4, 3, 2, 1 );
    //registers.GPR[ 2 ].f =  _mm_set_ps( 40, 30, 20, 10 );
    //registers.GPR[ 3 ].f =  _mm_set_ps1( 0 );
    //registers.GPR[ 4 ].f =  _mm_set_ps1( 0 );

    Instruction insts[ 16 ];
    Instruction* ptr = &insts[ 0 ];

    ptr->op = OP_SET;
    ptr->dst = 0;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 4;
    f32* floats = ( ( f32* )ptr ) + 3;
    floats[ 0 ] = 0.0f; floats[ 1 ] = 0.0f; floats[ 2 ] = 0.0f; floats[ 3 ] = 0.0f;
    ptr++;

    ptr->op = OP_SET;
    ptr->dst = 1;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 4;
    floats = ( ( f32* )ptr ) + 3;
    floats[ 0 ] = 1.0f; floats[ 1 ] = 2.0f; floats[ 2 ] = 3.0f; floats[ 3 ] = 4.0f;
    ptr++;

    ptr->op = OP_SET;
    ptr->dst = 2;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 4;
    floats = ( ( f32* )ptr ) + 3;
    floats[ 0 ] = 10.0f; floats[ 1 ] = 20.0f; floats[ 2 ] = 30.0f; floats[ 3 ] = 40.0f;
    ptr++;

    ptr->op = OP_SET;
    ptr->dst = 3;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 4;
    floats = ( ( f32* )ptr ) + 3;
    floats[ 0 ] = 0.0f; floats[ 1 ] = 0.0f; floats[ 2 ] = 0.0f; floats[ 3 ] = 0.0f;
    ptr++;

    ptr->op = OP_SET;
    ptr->dst = 4;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 4;
    floats = ( ( f32* )ptr ) + 2;
    floats[ 0 ] = 0.0f; floats[ 1 ] = 0.0f; floats[ 2 ] = 0.0f; floats[ 3 ] = 0.0f;
    ptr++;

    ptr->op = OP_ADD;
    ptr->dst = 0;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100111;
    ptr->dstSwizzle.activeNum = 2;
    ptr->src0 = 1;
    ptr->src0Type = REGISTER_GPR;
    ptr->src0Swizzle.swizzle = 0b11101100;
    ptr->src1 = 2;
    ptr->src1Type = REGISTER_GPR;
    ptr->src1Swizzle.swizzle = 0b11100110;
    ptr++;

    ptr->op = OP_DOT;
    ptr->dst = 3;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 1;
    ptr->src0 = 1;
    ptr->src0Type = REGISTER_GPR;
    ptr->src0Swizzle.swizzle = 0b11100100;
    ptr->src0Swizzle.activeNum = 2;
    ptr->src1 = 2;
    ptr->src1Type = REGISTER_GPR;
    ptr->src1Swizzle.swizzle = 0b11101110;
    ptr->src1Swizzle.activeNum = 2;
    ptr++;

    ptr->op = OP_DOT;
    ptr->dst = 4;
    ptr->dstType = REGISTER_GPR;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 2;
    ptr->src0 = 1;
    ptr->src0Type = REGISTER_GPR;
    ptr->src0Swizzle.swizzle = 0b11100100;
    ptr->src0Swizzle.activeNum = 3;
    ptr->src1 = 2;
    ptr->src1Type = REGISTER_GPR;
    ptr->src1Swizzle.swizzle = 0b11101110;
    ptr->src1Swizzle.activeNum = 3;
    ptr++;

    ptr->op = OP_RET;
    ptr->dst = 0;
    ptr->dstType = REGISTER_GPR;
    ptr->src0 = 0;
    ptr->src0Type = REGISTER_GPR;
    ptr->src1 = 0;
    ptr->src1Type = REGISTER_GPR;

    Shader shader;
    shader.instructions = &insts[ 0 ];
    shader.instructionsNum = 8;
    Execute( registers, shader );


    free( registers.IR );
    free( registers.OR );
    free( registers.GPR );
    return 0;
}
