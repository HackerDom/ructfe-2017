#pragma once
#include <cstdint>
#include <xmmintrin.h>
#include <malloc.h>
#include <string.h>
#include "png.h"

using u8    = uint8_t;
using i8    = int8_t;
using u16   = uint16_t;
using i16   = int16_t;
using u32   = uint32_t;
using i32   = int32_t;
using u64   = uint64_t;
using i64   = int64_t;
using f32   = float;
using f64   = double;

//
union __m128_union
{
    __m128 	f;
    __m128d d;
    __m128i i;
    __m64 	m64[ 2 ];
    u64 m128_u64[ 2 ];
    i64 m128_i64[ 2 ];
    f64 m128_f64[ 2 ];
    u32 m128_u32[ 4 ];
    i32 m128_i32[ 4 ];
    f32 m128_f32[ 4 ];
    u16 m128_u16[ 8 ];
    i16 m128_i16[ 8 ];
    u8 	m128_u8[ 16 ];
    i8 	m128_i8[ 16 ];

    inline operator __m128() { return f; }
};


//
enum OPERANDS
{
    OPERAND_DST  = 1 << 0,
    OPERAND_SRC0 = 1 << 1,
    OPERAND_SRC1 = 1 << 2,
};


//
#define OPS_DEFINE( YOUR_DEFINE ) \
    YOUR_DEFINE( OP_SET,  	"set"   , OPERAND_DST ) \
    YOUR_DEFINE( OP_SETI, 	"seti"	, OPERAND_DST ) \
    YOUR_DEFINE( OP_ADD,	"add"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_ADDI,	"addi"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_SUB,	"sub"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_SUBI,	"subi"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_MUL,	"mul"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_MULI,	"muli"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_DIV,	"div"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_DIVI,	"divi"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_DOT,	"dot"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_LENGTH, "length", OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_NORMALIZE, "normalize", OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_ABS,    "abs"   , OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_SATURATE, "saturate", OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_MOV,	"mov"	, OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_CVTFI,	"cvtfi"	, OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_CVTIF,	"cvtif"	, OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_TFETCH,	"tfetch", OPERAND_DST | OPERAND_SRC0 ) \
    YOUR_DEFINE( OP_CMPEQ,  "cmpeq",  OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPLT,  "cmplt",  OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPLE,  "cmple",  OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPGT,  "cmpgt",  OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPGE,  "cmpge",  OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPEQI, "cmpeqi", OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPLTI, "cmplti", OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_CMPGTI, "cmpgti", OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_JMP_TRUE, "jmp_true", 0 ) \
    YOUR_DEFINE( OP_JMP_FALSE, "jmp_false", 0 ) \
    YOUR_DEFINE( OP_OR,     "or"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_AND,	"and"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_XOR,	"xor"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_SHL,	"shl"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_SHR,	"shr"	, OPERAND_DST | OPERAND_SRC0 | OPERAND_SRC1 ) \
    YOUR_DEFINE( OP_RET,	"ret"   , 0 )


enum OP
{
    OP_INVALID = 0,
#define DEFINE_OP( ENUM_MEMBER, STR, OPERANDS_MASK ) ENUM_MEMBER,
	OPS_DEFINE( DEFINE_OP )
#undef DEFINE_OP
	
    OP_COUNT
};


//
static const char* g_opToStr[] = {
	"inv",
#define DEFINE_OPTOSTR( ENUM_MEMBER, STR, OPERANDS_MASK ) STR,
	OPS_DEFINE( DEFINE_OPTOSTR )
#undef DEFINE_OPTOSTR
};


//
static u32 g_opOperands[] = {
    0,
#define DEFINE_OPERANDS_MASK( ENUM_MEMBER, STR, OPERANDS_MASK ) OPERANDS_MASK,
    OPS_DEFINE( DEFINE_OPERANDS_MASK )
#undef DEFINE_OPTOSTR
};


//
enum REGISTER_TYPE
{
    REGISTER_IR = 0,
    REGISTER_OR,
    REGISTER_CR,
    REGISTER_GPR,
    REGISTER_TR,

    REGISTER_TYPES_NUM
};


//
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


//
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
};


//
struct SetInstruction
{
    OP op;
    // dst register
    struct
    {
        u32 dstType : 2;
        u32 dst : 30;
    };
    Swizzle dstSwizzle;
    union
    {
        f32 floats[ 4 ];
        i32 ints[ 4 ];
    };
};


//
struct TFetchInstruction
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
    // texture register
    u32 textureReg;
    u16 padding;
};


//
struct JumpInstruction
{
    OP op;
    i8 offset;
    u8 padding[ 23 ];
};
static_assert( sizeof( Instruction ) == 28, "" );
static_assert( sizeof( SetInstruction ) == 28, "" );
static_assert( sizeof( TFetchInstruction ) == 28, "" );
static_assert( sizeof( JumpInstruction ) == 28, "" );


//
enum ShaderType : u32
{
	SHADER_VERTEX = 0,
	SHADER_PIXEL
};


//
struct NonMovable
{
    NonMovable() = default;
    NonMovable( const NonMovable& ) = delete;
    NonMovable( const NonMovable&& ) = delete;
    NonMovable& operator=( const NonMovable& ) = delete;
    NonMovable& operator=( const NonMovable&& ) = delete;
};


//
struct Shader : public NonMovable
{
    Instruction* instructions;

    struct Header
    {
        struct
        {
            u32 type : 1;
            u32 instructionsNum : 10;
        };
        union
        {
            struct
            {
                u32 varyingsNum : 4;
                u32 padding : 28;
            } vs;
            struct
            {
                u32 padding : 32;
            } ps;
            u32 flags;
        };
    };
    Header header;

    Shader()
        : instructions( nullptr )
    {
        header.type = SHADER_VERTEX;
        header.instructionsNum = 0;
        header.flags = 0;
    }

    Shader( const char* fileName ) 
		: Shader()
	{
        FILE* f = fopen( fileName, "r" );
		if( !f )
			return;
        //
        fread( &header, sizeof( Header ), 1, f );
        //
        instructions = ( Instruction* )memalign( 16, header.instructionsNum * sizeof( Instruction ) );
        fread( instructions, sizeof( Instruction ), header.instructionsNum, f );
        fclose( f );
    }

    Shader( const u8* shader ) {
        const u8* ptr = shader;
        memcpy( &header, ptr, sizeof( Header ) );
        ptr += sizeof( Header );
        instructions = ( Instruction* )memalign( 16, header.instructionsNum * sizeof( Instruction ) );
        memcpy( instructions, ptr, header.instructionsNum * sizeof( Instruction ) );
    }

    size_t GetSize() const {
        return sizeof( Header ) + header.instructionsNum * sizeof( Instruction );
    }

    static bool IsValidPixelShader( const u8* shader ) {
        Header* _header;
        const u8* ptr = shader;
        _header = ( Header* )ptr;
        ptr += sizeof( Header );

        if( _header->type != SHADER_PIXEL )
            return false;

        if( _header->instructionsNum > 1024 )
            return false;
		
		Instruction* instructions = ( Instruction* )( shader + sizeof( Header ) );
		for( u32 ip = 0, iter = 0; ip < _header->instructionsNum; ip++ ) {
			Instruction& i = instructions[ ip ];
			if( i.op < 0 || i.op >= OP_COUNT ) 
				return false;
		}

        return true;
    }

    ~Shader() {
        if( instructions )
            free( instructions );
    }
};


//
struct VertexBuffer : public NonMovable
{
    u32 vertexNum;
    u32 vertexComponents;
    __m128_union* vertices;

    VertexBuffer()
        : vertexNum( 0 ), vertexComponents( 0 ), vertices( nullptr )
    {}

    VertexBuffer( u32 vertexNum, u32 vertexComponents ) {
        this->vertexNum = vertexNum;
        this->vertexComponents = vertexComponents;
        vertices = ( __m128_union* )memalign( 16, vertexNum * vertexComponents * sizeof( __m128 ) );
    }

    ~VertexBuffer() {
        if( !vertices )
            free( vertices );
    }
};


//
struct IndexBuffer : public NonMovable
{
    u32 indicesNum;
    u32* indices;

    IndexBuffer()
        : indicesNum( 0 ), indices( nullptr )
    {}

    IndexBuffer( u32 indicesNum ) {
        this->indicesNum = indicesNum;
        this->indices = ( u32* )memalign( 16, indicesNum * sizeof( u32 ) );
    }

    ~IndexBuffer() {
        if( indices )
            free( indices );
    }
};


//
struct PipelineState
{
     __m128_union constants[ 256 ];
     Image* textures[ 16 ];
     VertexBuffer* vb;
     IndexBuffer* ib;
     Shader* vs;
     Shader* ps;
     Image* rt;
     Image* depthRt;

     PipelineState() {
         memset( this, 0, sizeof( PipelineState ) );
     }
};

//
void ClearRenderTarget( Image* rt, u8 r , u8 g, u8 b, u8 a );
void ClearDepthRenderTarget(Image* depthRt, float value );
void Draw( const PipelineState& pState );
