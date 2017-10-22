#include <stdio.h>
#include <string.h>
#include "types.h"

//
const char* g_opToStr[] = {
    "inv",
    "set",
    "add",
    "sub",
    "mul",
    "div",
    "dot",
    "mov",
    "ret"
};


//
char SwizzleToChar( u8 s ) {
    if( s == 0 ) return 'x';
    if( s == 1 ) return 'y';
    if( s == 2 ) return 'z';
    if( s == 3 ) return 'w';
}


//
void DumpRegister( REGISTER_TYPE type, u32 idx, Swizzle swizzle ) {
    if( type == REGISTER_IR )
        printf( "i" );
    if( type == REGISTER_OR )
        printf( "o" );
    if( type == REGISTER_CR )
        printf( "c" );
    if( type == REGISTER_GPR )
        printf( "r" );

    printf( "%u.", idx );

    if( swizzle.activeNum >= 1 )
        printf( "%c", SwizzleToChar( swizzle.i0 ) );
    if( swizzle.activeNum >= 2 )
        printf( "%c", SwizzleToChar( swizzle.i1 ) );
    if( swizzle.activeNum >= 3 )
        printf( "%c", SwizzleToChar( swizzle.i2 ) );
    if( swizzle.activeNum >= 4 )
        printf( "%c", SwizzleToChar( swizzle.i3 ) );
    printf( " " );
}


//
int main( int argc, char* argv[] ) {
    Shader shader( argv[ 1 ] );

    printf( "Instructions num: %u\n", shader.header.instructionsNum );
    if( shader.header.type == 0 ) {
        printf( "VS flags:\n" );
        printf( "\tVS_VARYINGS_NUM = %u\n", shader.header.vs.varyingsNum );
    }
    if( shader.header.type == 1 ) {
        printf( "PS flags:\n" );
        printf( "\tPS_INTEGER_OUTPUT = %u\n", shader.header.ps.integerOutput );
    }

    //
    for( u32 i = 0; i < shader.header.instructionsNum; i++ ){
        Instruction& inst = shader.instructions[ i ];

        printf( "%s ", g_opToStr[ inst.op ] );
        if( inst.op == OP_SET ) {
            DumpRegister( ( REGISTER_TYPE )inst.dstType, inst.dst, inst.dstSwizzle );

            f32* floats = ( ( f32* )&inst ) + 3;
            for( u32 i = 0; i < inst.dstSwizzle.activeNum; i++ )
                printf( "%f ", floats[ i ] );
        } else if( inst.op == OP_RET ) {
        } else if( inst.op == OP_MOV ) {
            DumpRegister( ( REGISTER_TYPE )inst.dstType, inst.dst, inst.dstSwizzle );
            DumpRegister( ( REGISTER_TYPE )inst.src0Type, inst.src0, inst.src0Swizzle );
        } else {
            DumpRegister( ( REGISTER_TYPE )inst.dstType, inst.dst, inst.dstSwizzle );
            DumpRegister( ( REGISTER_TYPE )inst.src0Type, inst.src0, inst.src0Swizzle );
            DumpRegister( ( REGISTER_TYPE )inst.src1Type, inst.src1, inst.src1Swizzle );
        }
        printf( "\n" );
    }
    return 0;
}
