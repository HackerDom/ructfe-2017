#include <iostream>
#include <malloc.h>
#include "types.h"

__m128_union* registers;

enum OP : u8
{
    OP_INVALID = 0,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_DOT,

    OP_RET,

    OP_COUNT
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
    i16 dst;
    Swizzle dstSwizzle;
    i16 src0;
    Swizzle src0Swizzle;
    u16 src1;
    Swizzle src1Swizzle;
};


//
bool Execute( Instruction* instructions, u16 num ) {

    for( u16 ip = 0; /*ip < num*/; ip++ )
    {
        Instruction& i = instructions[ ip ];

        __m128_union src0;
        src0.m128_f32[ 0 ] = registers[ i.src0 ].m128_f32[ i.src0Swizzle.i0 ];
        src0.m128_f32[ 1 ] = registers[ i.src0 ].m128_f32[ i.src0Swizzle.i1 ];
        src0.m128_f32[ 2 ] = registers[ i.src0 ].m128_f32[ i.src0Swizzle.i2 ];
        src0.m128_f32[ 3 ] = registers[ i.src0 ].m128_f32[ i.src0Swizzle.i3 ];

        __m128_union src1;
        src1.m128_f32[ 0 ] = registers[ i.src1 ].m128_f32[ i.src1Swizzle.i0 ];
        src1.m128_f32[ 1 ] = registers[ i.src1 ].m128_f32[ i.src1Swizzle.i1 ];
        src1.m128_f32[ 2 ] = registers[ i.src1 ].m128_f32[ i.src1Swizzle.i2 ];
        src1.m128_f32[ 3 ] = registers[ i.src1 ].m128_f32[ i.src1Swizzle.i3 ];

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
            case OP_RET:
                return true;
        }

        __m128_union& dst = registers[ i.dst ];
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



using namespace std;

int main()
{
    registers = ( __m128_union* )memalign( 16, 256 );

    //add dst.xyzw src0.xyzw src1.xyzw
    //add dst.x src0.x src1.y  		: add dst.x src0.xyzw src1.yyzw
    //add dst.yx src0.xw src1.zy	: add dst.yx src0.xwzw src1.zyzw ( 1, 4 ) + ( 30, 20 ) = ( x, x, 31, 24 )
    //add dst.wy src0.xw src1.zy	: add dst.yx src0.xwzw src1.zyzw ( 1, 4 ) + ( 30, 20 ) = ( 31, x, 24, x )
    //dot dst.x src0.xy src1.zw     1 * 30 + 2 * 40 = 30 + 80 = 110
    //dot dst.xy src0.xyz src1.zwz  1 * 30 + 2 * 40 + 3 * 30 = 110 + 90 = 200

    registers[ 0 ].f =  _mm_set_ps1( 0 );
    registers[ 1 ].f =  _mm_set_ps( 4, 3, 2, 1 );
    registers[ 2 ].f =  _mm_set_ps( 40, 30, 20, 10 );
    registers[ 3 ].f =  _mm_set_ps1( 0 );
    registers[ 4 ].f =  _mm_set_ps1( 0 );

    Instruction insts[ 8 ];
    Instruction* ptr = &insts[ 0 ];

    ptr->op = OP_ADD;
    ptr->dst = 0;
    ptr->dstSwizzle.swizzle = 0b11100111;
    ptr->dstSwizzle.activeNum = 2;
    ptr->src0 = 1;
    ptr->src0Swizzle.swizzle = 0b11101100;
    ptr->src1 = 2;
    ptr->src1Swizzle.swizzle = 0b11100110;
    ptr++;

    ptr->op = OP_DOT;
    ptr->dst = 3;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 1;
    ptr->src0 = 1;
    ptr->src0Swizzle.swizzle = 0b11100100;
    ptr->src0Swizzle.activeNum = 2;
    ptr->src1 = 2;
    ptr->src1Swizzle.swizzle = 0b11101110;
    ptr->src1Swizzle.activeNum = 2;
    ptr++;

    ptr->op = OP_DOT;
    ptr->dst = 4;
    ptr->dstSwizzle.swizzle = 0b11100100;
    ptr->dstSwizzle.activeNum = 2;
    ptr->src0 = 1;
    ptr->src0Swizzle.swizzle = 0b11100100;
    ptr->src0Swizzle.activeNum = 3;
    ptr->src1 = 2;
    ptr->src1Swizzle.swizzle = 0b11101110;
    ptr->src1Swizzle.activeNum = 3;
    ptr++;

    ptr->op = OP_RET;
    ptr->dst = 0;
    ptr->src0 = 0;
    ptr->src1 = 0;

    Execute( insts,0 );


    free( registers );
    return 0;
}
