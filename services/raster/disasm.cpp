#include <stdio.h>
#include <string.h>
#include "gpu.h"


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
	if( argc < 2 ) {
		printf( "./disasm <input>\n" );
		return 1;
	}
    Shader shader( argv[ 1 ] );
	if( !shader.instructions ) {
		printf( "Invalid shader\n" );
		return 1;
	}

    printf( "Instructions num: %u\n", shader.header.instructionsNum );
    if( shader.header.type == SHADER_VERTEX ) {
        printf( "VS flags:\n" );
        printf( "\tVS_VARYINGS_NUM = %u\n", shader.header.vs.varyingsNum );
    }
    if( shader.header.type == SHADER_PIXEL ) {
        printf( "PS flags:\n" );
		printf( "\t\n" );
    }

    //
    for( u32 i = 0; i < shader.header.instructionsNum; i++ ){
        Instruction& inst = shader.instructions[ i ];
		if( inst.op < 0 || inst.op >= OP_COUNT ) {
			printf( "Invalid instruction op code\n" );
			return 1;
		}

        printf( "%s ", g_opToStr[ inst.op ] );
        if( g_opOperands[ inst.op ] & OPERAND_DST )
            DumpRegister( ( REGISTER_TYPE )inst.dstType, inst.dst, inst.dstSwizzle );
        if( g_opOperands[ inst.op ] & OPERAND_SRC0 )
            DumpRegister( ( REGISTER_TYPE )inst.src0Type, inst.src0, inst.src0Swizzle );
        if( g_opOperands[ inst.op ] & OPERAND_SRC1 )
            DumpRegister( ( REGISTER_TYPE )inst.src1Type, inst.src1, inst.src1Swizzle );

        if( inst.op == OP_SET ) {
            SetInstruction* setInst = ( SetInstruction* )&inst;
            for( u32 i = 0; i < inst.dstSwizzle.activeNum; i++ )
                printf( "%f ", setInst->floats[ i ] );
        }
        if( inst.op == OP_SETI ) {
            SetInstruction* setInst = ( SetInstruction* )&inst;
            for( u32 i = 0; i < inst.dstSwizzle.activeNum; i++ )
                printf( "%d ", setInst->ints[ i ] );
        }
        if( inst.op == OP_TFETCH ) {
            TFetchInstruction* tfetch = ( TFetchInstruction* )&inst;
            printf( "t%u ", tfetch->textureReg );
        }
        if( inst.op == OP_JMP_TRUE || inst.op == OP_JMP_FALSE ) {
            JumpInstruction* jmp = ( JumpInstruction* )&inst;
            printf("%d ", jmp->offset );
        }
        printf( "\n" );
    }
    return 0;
}
