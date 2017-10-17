#include <iostream>
#include <malloc.h>
#include "types.h"

enum OP
{
    OP_INVALID = 0,
    OP_SET,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_DOT,
    OP_MOV,

    OP_RET,

    OP_COUNT
};

enum REGISTER_TYPE
{
    REGISTER_IR = 0,
    REGISTER_OR,
    REGISTER_CR,
    REGISTER_GPR,

    REGISTER_TYPES_NUM
};

struct Swizzle
{
    union
    {
        struct
        {
            u8 i0 : 2;
            u8 i1 : 2;
            u8 i2 : 2;
            u8 i3 : 2;
        };
        u8 swizzle;
    };
    u8 activeNum;

    Swizzle()
    {
        swizzle = 0b11100100;
        activeNum = 4;
    }
};

struct Instruction
{
    OP op;
    // dst register
    struct
    {
        u32 dstType : 2;
        u32 dst : 30;
    };
    Swizzle dstSwizzle;
    // src0 register
    struct
    {
        u32 src0Type : 2;
        u32 src0 : 30;
    };
    Swizzle src0Swizzle;
    // src1 register
    struct
    {
        u32 src1Type : 2;
        u32 src1 : 30;
    };
    Swizzle src1Swizzle;
    u32 padding;
};
static_assert( sizeof( Instruction ) == 32, "" );


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
};


//
struct RenderTarget
{
    u16 width;
    u16 height;
    __m128_union* pixels;
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
void LoadRegister( __m128_union& output, const Registers& registers, REGISTER_TYPE regType, u32 regIdx, Swizzle regSwizzle ) {
    output.m128_f32[ 0 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i0 ];
    output.m128_f32[ 1 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i1 ];
    output.m128_f32[ 2 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i2 ];
    output.m128_f32[ 3 ] = registers.regs[ regType ][ regIdx ].m128_f32[ regSwizzle.i3 ];
}


inline
void StoreRegister( Registers& registers, REGISTER_TYPE regType, u32 regIdx, Swizzle regSwizzle, const __m128_union& input ) {
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

        __m128_union src0;
        src0.m128_f32[ 0 ] = registers.regs[ i.src0Type ][ i.src0 ].m128_f32[ i.src0Swizzle.i0 ];
        src0.m128_f32[ 1 ] = registers.regs[ i.src0Type ][ i.src0 ].m128_f32[ i.src0Swizzle.i1 ];
        src0.m128_f32[ 2 ] = registers.regs[ i.src0Type ][ i.src0 ].m128_f32[ i.src0Swizzle.i2 ];
        src0.m128_f32[ 3 ] = registers.regs[ i.src0Type ][ i.src0 ].m128_f32[ i.src0Swizzle.i3 ];

        __m128_union src1;
        src1.m128_f32[ 0 ] = registers.regs[ i.src1Type ][ i.src1 ].m128_f32[ i.src1Swizzle.i0 ];
        src1.m128_f32[ 1 ] = registers.regs[ i.src1Type ][ i.src1 ].m128_f32[ i.src1Swizzle.i1 ];
        src1.m128_f32[ 2 ] = registers.regs[ i.src1Type ][ i.src1 ].m128_f32[ i.src1Swizzle.i2 ];
        src1.m128_f32[ 3 ] = registers.regs[ i.src1Type ][ i.src1 ].m128_f32[ i.src1Swizzle.i3 ];

        __m128_union result;

        switch( i.op )
        {
            case OP_INVALID:
#if DEBUG
                printf( "Invalid op\n" );
#endif
                return false;
            case OP_ADD:
                result.f = _mm_add_ps( src0, src1 );
                break;
            case OP_SUB:
                result.f = _mm_sub_ps( src0, src1 );
                break;
            case OP_MUL:
                result.f = _mm_mul_ps( src0, src1 );
                break;
            case OP_DIV:
                result.f = _mm_div_ps( src0, src1 );
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
            case OP_MOV:
                result.f = src0.f;
                break;
            case OP_RET:
                return true;
        }

        __m128_union& dst = registers.regs[ i.dstType ][ i.dst ];
        if( i.dstSwizzle.activeNum >= 1 )
            dst.m128_f32[ i.dstSwizzle.i0 ] = result.m128_f32[ 0 ];
        if( i.dstSwizzle.activeNum >= 2 )
            dst.m128_f32[ i.dstSwizzle.i1 ] = result.m128_f32[ 1 ];
        if( i.dstSwizzle.activeNum >= 3 )
            dst.m128_f32[ i.dstSwizzle.i2 ] = result.m128_f32[ 2 ];
        if( i.dstSwizzle.activeNum >= 4 )
            dst.m128_f32[ i.dstSwizzle.i3 ] = result.m128_f32[ 3 ];
    }

    return true;
}

void Draw(  __m128_union* constants, const Shader& vs, const VertexBuffer& vb, const RenderTarget& rt )
{
    __m128_union* GPR = ( __m128_union* )memalign( 16, 256 * sizeof( __m128 ) );
    const u32 VARYINGS_PER_VERTEX = 4;
    // 4 varyings for each vertex of triangle = 12 varyings per triangle
    __m128_union varyings[ VARYINGS_PER_VERTEX * 3 ];

    for( u32 t = 0; t < vb.vertexNum / 3; t++ )
    {
        // vertex shader stage
        __m128_union* vsInput = &vb.vb[ 3 * vb.vertexComponents * t ];
        i16 minX = 8192;
        i16 minY = 8192;
        i16 maxX = 0;
        i16 maxY = 0;
        i16 X[ 3 ], Y[ 3 ];
        f32 Z[ 3 ];
        //f32 W[ 3 ];
        for( u32 v = 0; v < 3; v++ )
        {
            Registers vsRegs;
            vsRegs.IR = vsInput;
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
            __m128 tmp = _mm_mul_ps( pos, _mm_set_ps( 0.5f, -0.5f, 1.0f, 1.0f ) );
            tmp = _mm_add_ps( pos, _mm_set_ps( 0.5f, 0.5f, 0.0f, 0.0f ) );
            pos.f = _mm_mul_ps( pos, _mm_set_ps( rt.width, rt.height, 1.0f, 1.0f ) );
            X[ v ] = pos.m128_f32[ 0 ] + 0.5f;
            Y[ v ] = pos.m128_f32[ 1 ] + 0.5f;
            Z[ v ] = pos.m128_f32[ 2 ];
            // tri bounds
            if( X[ v ] > maxX ) maxX = X[ v ];
            if( Y[ v ] > maxY ) maxY = Y[ v ];
            if( X[ v ] < minX ) minX = X[ v ];
            if( Y[ v ] < minY ) minY = Y[ v ];
        }

        // fixed function stage
        int triArea = (X[1] - X[0]) * (Y[2] - Y[0]) - (X[0] - X[2]) * (Y[0] - Y[1]);
        if( triArea <= 0 )
            continue;


    }

    free( GPR );
}

int main()
{
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

    registers.GPR[ 0 ].f =  _mm_set_ps1( 0 );
    registers.GPR[ 1 ].f =  _mm_set_ps( 4, 3, 2, 1 );
    registers.GPR[ 2 ].f =  _mm_set_ps( 40, 30, 20, 10 );
    registers.GPR[ 3 ].f =  _mm_set_ps1( 0 );
    registers.GPR[ 4 ].f =  _mm_set_ps1( 0 );

    Instruction insts[ 8 ];
    Instruction* ptr = &insts[ 0 ];

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
