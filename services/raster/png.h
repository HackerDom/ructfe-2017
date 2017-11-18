#pragma once
#include <stdint.h>
#include <malloc.h>
#define STBI_ONLY_PNG 1
#include "stb_image.h"
#include "stb_image_write.h"


//
union RGBA
{
	struct
	{
		uint32_t r : 8;
		uint32_t g : 8;
		uint32_t b : 8;
		uint32_t a : 8;
	};
	uint32_t rgba;
};


//
struct Image
{
    union
    {
        RGBA*		rgba;
        float*      f32;
    };
    uint32_t 	width;
    uint32_t 	height;

    Image()
    	: rgba( nullptr ), width( 0 ), height( 0 )
    {

    }

    Image( uint32_t w, uint32_t h )
    	: rgba( nullptr ), width( w ), height( h )
    {
        uint32_t size = w * h * sizeof( RGBA );
        size = ( size + 15 ) & ~15;
        rgba = ( RGBA* )memalign( 16, size );
    }

    Image( const Image& ) = delete;
    Image( const Image&& ) = delete;
    Image& operator=( const Image& ) = delete;
    Image& operator=( const Image&& ) = delete;

    ~Image()
    {
        free( rgba );
    }

    //
    void Reinit( uint32_t w, uint32_t h )
    {
        free( rgba );
        width = w;
        height = h;
        uint32_t size = w * h * sizeof( RGBA );
        size = ( size + 15 ) & ~15;
        rgba = ( RGBA* )memalign( 16, size );
    }
};


//
bool read_png( const char* file_name, Image& image );
bool save_png( const char* file_name, const Image& image );
bool save_png( const char* file_name, const RGBA* rgba, uint32_t width, uint32_t height );
