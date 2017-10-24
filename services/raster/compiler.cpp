#include <stdio.h>
#include <string.h>
#include <fstream>
#include <vector>
#include "types.h"


//
u8 CharToSwizzle( char c ) {
    switch ( c )
    {
        case 'x': return 0;
        case 'y': return 1;
        case 'z': return 2;
        case 'w': return 3;
    }

    return 0;
}


//
void ParseRegister( const std::string& str, REGISTER_TYPE& type, u32& idx, Swizzle& swizzle ) {
    char copy[ 16 ];
    strcpy( copy, str.c_str() );
    const char* idxStr = &copy[ 1 ];

    if( copy[ 0 ] == 'i' )
        type = REGISTER_IR;
    if( copy[ 0 ] == 'o' )
        type = REGISTER_OR;
    if( copy[ 0 ] == 'c' )
        type = REGISTER_CR;
    if( copy[ 0 ] == 'r' )
        type = REGISTER_GPR;

    char* dot = const_cast< char* >( strchr( idxStr, '.' ) );
    *dot = 0;
    idx = atoi( idxStr );

    const char* swizzleStr = dot + 1;
    swizzle.activeNum = strlen( swizzleStr );
    if( swizzle.activeNum >= 1 )
        swizzle.i0 = CharToSwizzle( swizzleStr[ 0 ] );
    if( swizzle.activeNum >= 2 )
        swizzle.i1 = CharToSwizzle( swizzleStr[ 1 ] );
    if( swizzle.activeNum >= 3 )
        swizzle.i2 = CharToSwizzle( swizzleStr[ 2 ] );
    if( swizzle.activeNum >= 4 )
        swizzle.i3 = CharToSwizzle( swizzleStr[ 3 ] );
}


//
int main( int argc, char* argv[] ) {
    if( argc < 4 ) {
		printf( "./compiler <vs|ps> <input> <output>\n" );
        return 1;
	}

    const char* type = argv[ 1 ];
    const char* input = argv[ 2 ];
    const char* output = argv[ 3 ];

    //
    Shader::Header header;
    if( strcmp( type, "vs" ) == 0 )
        header.type = SHADER_VERTEX;
    else if( strcmp( type, "ps" ) == 0 )
        header.type = SHADER_PIXEL;
    else {
        printf( "Invalid shader type\n" );
        return 1;
    }

    std::ifstream infile( input );
    std::vector< Instruction > insts;
    //
    while( !infile.eof() ) {
        Instruction inst;
        std::string opStr;
        infile >> opStr;

        if( opStr.empty() )
            continue;

        if( opStr.compare( "VS_VARYINGS_NUM" ) == 0 ) {
            u32 varyingsNum;
            infile >> varyingsNum;
            header.vs.varyingsNum = varyingsNum;
            continue;
        }

        inst.op = OP_INVALID;
        for( u32 i = 0; i < OP_COUNT; i++ ){
            if( opStr.compare( g_opToStr[ i ] ) == 0 ) {
                inst.op = ( OP )i;
                break;
            }
        }

        if( inst.op == OP_INVALID ) {
            printf( "Invalid op: %s\n", opStr.c_str() );
            return 1;
        }

        std::string str;
        REGISTER_TYPE regType;
        u32 reg;
        if( g_opOperands[ inst.op ] & OPERAND_DST ) {
            infile >> str;
            ParseRegister( str,  regType, reg, inst.dstSwizzle );
            inst.dst = reg;
            inst.dstType = regType;
        }

        if( g_opOperands[ inst.op ] & OPERAND_SRC0 ) {
            infile >> str;
            ParseRegister( str,  regType, reg, inst.src0Swizzle );
            inst.src0 = reg;
            inst.src0Type = regType;
        }

        if( g_opOperands[ inst.op ] & OPERAND_SRC1 ) {
            infile >> str;
            ParseRegister( str,  regType, reg, inst.src1Swizzle );
            inst.src1 = reg;
            inst.src1Type = regType;
        }

        if( inst.op == OP_SET ) {
            SetInstruction* setInst = ( SetInstruction* )&inst;
            for( u32 i = 0; i < inst.dstSwizzle.activeNum; i++ )
                infile >> setInst->floats[ i ];
        }

        if( inst.op == OP_SETI ) {
            SetInstruction* setInst = ( SetInstruction* )&inst;
            for( u32 i = 0; i < inst.dstSwizzle.activeNum; i++ )
                infile >> setInst->ints[ i ];
        }

        insts.push_back( inst );
    }

    header.instructionsNum = insts.size();

    FILE* binary = fopen( output, "w" );
    fwrite( &header, sizeof( Shader::Header ), 1, binary );
    fwrite( insts.data(), sizeof( Instruction ), insts.size(), binary );
    fclose( binary );
    return 0;
}
