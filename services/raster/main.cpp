#include "gpu.h"

void DrawTest()
{
    Image image( 256, 256 );
    Shader vs( "shaders/simple.vs.bin" );
    Shader ps( "shaders/draw_test.ps.bin" );

    VertexBuffer vb( 4, 2 );
    vb.vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  -1.0f );
    vb.vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f,  0.0f,  1.0f );

    vb.vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f, -1.0f );
    vb.vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  0.0f );

    vb.vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  1.0f );
    vb.vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 1.0f, 1.0f,  0.0f,  0.0f );

    vb.vertices[ 3 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  1.0f );
    vb.vertices[ 3 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  0.0f );

    IndexBuffer ib( 6 );
    ib.indices[ 0 ] = 0;
    ib.indices[ 1 ] = 1;
    ib.indices[ 2 ] = 2;
    ib.indices[ 3 ] = 0;
    ib.indices[ 4 ] = 2;
    ib.indices[ 5 ] = 3;

    PipelineState pState;
    pState.vb = &vb;
    pState.ib = &ib;
    pState.vs = &vs;
    pState.ps = &ps;
    pState.rt = &image;
    Draw( pState );
    save_png( "test.png", image );
}

void TextureTest()
{
    Image image( 256, 256 );
    Image texture;
    read_png( "texture.png", texture );
    Shader vs( "shaders/simple.vs.bin" );
    Shader ps( "shaders/texture_test.ps.bin" );

    VertexBuffer vb( 4, 2 );
    vb.vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  -1.0f );
    vb.vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  0.0f );

    vb.vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f, -1.0f );
    vb.vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  0.0f );

    vb.vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  1.0f );
    vb.vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  1.0f );

    vb.vertices[ 3 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  1.0f );
    vb.vertices[ 3 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  1.0f );

    IndexBuffer ib( 6 );
    ib.indices[ 0 ] = 0;
    ib.indices[ 1 ] = 1;
    ib.indices[ 2 ] = 2;
    ib.indices[ 3 ] = 0;
    ib.indices[ 4 ] = 2;
    ib.indices[ 5 ] = 3;

    PipelineState pState;
    pState.vb = &vb;
    pState.ib = &ib;
    pState.vs = &vs;
    pState.textures[ 0 ] = &texture;
    pState.ps = &ps;
    pState.rt = &image;
    Draw( pState );
    save_png( "texture_test.png", image );
}


//
void GpuTests()
{
    DrawTest();
    TextureTest();
}


//
void Service()
{

}


int main()
{
    GpuTests();
    return 0;
}
