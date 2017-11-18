#include "gpu.h"
#include "httpserver.h"
#include "ship.h"
#include <lib3ds/file.h>
#include <lib3ds/node.h>
#include <lib3ds/mesh.h>
#include <lib3ds/vector.h>
#include <lib3ds/matrix.h>
#include <list>
#include <math.h>
#include <time.h>

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

    VertexBuffer vb( 6, 2 );
    vb.vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  -1.0f );
    vb.vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  0.0f );

    vb.vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f, -1.0f );
    vb.vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  0.0f );

    vb.vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  1.0f );
    vb.vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  1.0f );

    vb.vertices[ 3 * 2 + 0 ].f = vb.vertices[ 0 * 2 + 0 ].f;
    vb.vertices[ 3 * 2 + 1 ].f = vb.vertices[ 0 * 2 + 1 ].f;

    vb.vertices[ 4 * 2 + 0 ].f = vb.vertices[ 2 * 2 + 0 ].f;
    vb.vertices[ 4 * 2 + 1 ].f = vb.vertices[ 2 * 2 + 1 ].f;

    vb.vertices[ 5 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  1.0f );
    vb.vertices[ 5 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  1.0f );

    PipelineState pState;
    pState.vb = &vb;
    pState.ib = nullptr;
    pState.vs = &vs;
    pState.textures[ 0 ] = &texture;
    pState.ps = &ps;
    pState.rt = &image;
    Draw( pState );
    save_png( "texture_test.png", image );
}

void BuildViewMatrix( Lib3dsMatrix viewMatrix, Lib3dsVector eye, Lib3dsVector at, Lib3dsVector up ) {
    Lib3dsVector zAxis;
    lib3ds_vector_sub( zAxis, at, eye );
    lib3ds_vector_normalize( zAxis );

    Lib3dsVector xAxis, yAxis;
    lib3ds_vector_cross( xAxis, up, zAxis );
    lib3ds_vector_normalize( xAxis );
    lib3ds_vector_cross( yAxis, zAxis, xAxis );

    viewMatrix[ 0 ][ 0 ] = xAxis[ 0 ];
    viewMatrix[ 1 ][ 0 ] = xAxis[ 1 ];
    viewMatrix[ 2 ][ 0 ] = xAxis[ 2 ];
    viewMatrix[ 3 ][ 0 ] = -lib3ds_vector_dot( xAxis, eye );

    viewMatrix[ 0 ][ 1 ] = yAxis[ 0 ];
    viewMatrix[ 1 ][ 1 ] = yAxis[ 1 ];
    viewMatrix[ 2 ][ 1 ] = yAxis[ 2 ];
    viewMatrix[ 3 ][ 1 ] = -lib3ds_vector_dot( yAxis, eye );

    viewMatrix[ 0 ][ 2 ] = zAxis[ 0 ];
    viewMatrix[ 1 ][ 2 ] = zAxis[ 1 ];
    viewMatrix[ 2 ][ 2 ] = zAxis[ 2 ];
    viewMatrix[ 3 ][ 2 ] = -lib3ds_vector_dot( zAxis, eye );

    viewMatrix[ 0 ][ 3 ] = 0.0f;
    viewMatrix[ 1 ][ 3 ] = 0.0f;
    viewMatrix[ 2 ][ 3 ] = 0.0f;
    viewMatrix[ 3 ][ 3 ] = 1.0f;
}

void BuildOrthoProjMatrix( Lib3dsMatrix projMatrix, f32 width, f32 height, f32 near, f32 far ) {
    for( u32 i = 0; i < 4; i++ )
        for( u32 j = 0; j < 4; j++ )
            projMatrix[ i ][ j ] = 0.0f;

    projMatrix[ 0 ][ 0 ] = 2.0f / width;
    projMatrix[ 1 ][ 1 ] = 2.0f / height;
    projMatrix[ 2 ][ 2 ] = 1.0f / ( far - near );
    projMatrix[ 3 ][ 2 ] = near / ( near - far );
    projMatrix[ 3 ][ 3 ] = 1.0f;
}


void BuildProjMatrix( Lib3dsMatrix projMatrix, float fovY, float aspect, float near, float far ) {
    for( u32 i = 0; i < 4; i++ )
        for( u32 j = 0; j < 4; j++ )
            projMatrix[ i ][ j ] = 0.0f;

    f32 yScale = 1.0f / tanf( 0.5f * fovY );
    f32 xScale = yScale / aspect;
    f32 _22 = far / ( far - near );

    projMatrix[ 0 ][ 0 ] = xScale;
    projMatrix[ 1 ][ 1 ] = yScale;
    projMatrix[ 2 ][ 2 ] = _22;
    projMatrix[ 3 ][ 2 ] = -_22 * near;
    projMatrix[ 2 ][ 3 ] = 1.0f;
}


//
VertexBuffer* LoadShip()
{
    Lib3dsFile* file = lib3ds_file_load( "ship.3ds" );
    Lib3dsMesh* mesh = file->meshes;
    VertexBuffer* vb = new VertexBuffer( 3 * mesh->faces, 2 );

    //for( u32 f = 0; f < mesh->faces; f++ ) {
    //    Lib3dsFace& face = mesh->faceL[ f ];
    //    face.smoothing = 1;
    //}
    Lib3dsVector* normalL = new Lib3dsVector[ 3 * mesh->faces ];
    lib3ds_mesh_calculate_normals( mesh, normalL );

    u32 v = 0;
    for( u32 f = 0; f < mesh->faces; f++ ) {
        const Lib3dsFace& face = mesh->faceL[ f ];
        for( u32 p = 0; p < 3; p++ ) {
            Lib3dsVector& point = mesh->pointL[ face.points[ p ] ].pos;
            Lib3dsVector& normal = normalL[ f * 3 + p ];
            Lib3dsVector pt, n;
            Lib3dsMatrix identity;
            lib3ds_matrix_identity( identity );
            lib3ds_vector_transform( pt, identity, point );
            lib3ds_vector_transform( n,  identity, normal );
            vb->vertices[ v * vb->vertexComponents + 0 ].f = _mm_set_ps( 1.0f, pt[ 2 ], pt[ 1 ], pt[ 0 ] );
            vb->vertices[ v * vb->vertexComponents + 1 ].f = _mm_set_ps( 0.0f, n[ 2 ], n[ 1 ], n[ 0 ] );
            v++;
        }
    }
    lib3ds_file_free( file );

    return vb;
}


//
void DrawShip()
{
    VertexBuffer* vb = LoadShip();

    /*VertexBuffer vb( 6, 2 );
    vb.vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  -1.0f );
    vb.vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  0.0f );

    vb.vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f, -1.0f );
    vb.vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  0.0f );

    vb.vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f,  1.0f,  1.0f );
    vb.vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  1.0f );

    vb.vertices[ 3 * 2 + 0 ].f = vb.vertices[ 0 * 2 + 0 ].f;
    vb.vertices[ 3 * 2 + 1 ].f = vb.vertices[ 0 * 2 + 1 ].f;

    vb.vertices[ 4 * 2 + 0 ].f = vb.vertices[ 2 * 2 + 0 ].f;
    vb.vertices[ 4 * 2 + 1 ].f = vb.vertices[ 2 * 2 + 1 ].f;

    vb.vertices[ 5 * 2 + 0 ].f = _mm_set_ps( 1.0f, 0.0f, -1.0f,  1.0f );
    vb.vertices[ 5 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  1.0f );

    Image texture;
    read_png( "texture.png", texture );*/

    Lib3dsMatrix view, proj, viewProj;
    Lib3dsVector camPos, camAt, camUp;
    camPos[ 0 ] = 1.0f;
    camPos[ 1 ] = 1.0f;
    camPos[ 2 ] = -2.0f;
    camAt[ 0 ] = 0.0f;
    camAt[ 1 ] = 0.0f;
    camAt[ 2 ] = 0.0f;
    camUp[ 0 ] = 0.0f;
    camUp[ 1 ] = 1.0f;
    camUp[ 2 ] = 0.0f;
    BuildViewMatrix( view, camPos, camAt, camUp );
    BuildProjMatrix( proj, 90.0f / 180.0f * LIB3DS_PI, 1.0f, 0.1f, 100.0f );
    //BuildOrthoProjMatrix( proj, 4.0, 4.0, 0.1f, 100.0f );
    lib3ds_matrix_copy( viewProj, proj );
    lib3ds_matrix_mult( viewProj, view );
    lib3ds_matrix_transpose( viewProj );

    Image image( 512, 512 );
    Image depthRt( 512, 512 );
    Shader vs( "shaders/ship.vs.bin" );
    Shader ps( "shaders/ship.ps.bin" );

    PipelineState pState;
    memcpy( pState.constants, viewProj, 4 * 4 * sizeof( float ) );
    memcpy( &pState.constants[ 4 ], camPos, 4 * sizeof( float ) );
    pState.vb = vb;
    pState.ib = nullptr;
    pState.vs = &vs;
    //pState.textures[ 0 ] = &texture;
    pState.ps = &ps;
    pState.rt = &image;
    pState.depthRt = &depthRt;
    ClearDepthRenderTarget( pState.depthRt, 1.0f );
    Draw( pState );
    save_png( "ship.png", image );

    /*Lib3dsNode* nodes = file->nodes;
    std::list< Lib3dsNode* > stack;
    while( nodes ) {
        //
        if( node->type == LIB3DS_OBJECT_NODE ) {

        }

        // DFS
        if( nodes->childs ) {
            stack.push_back( nodes );
            nodes = nodes->childs;
        } else if( nodes->next ) {
            nodes = nodes->next;
        } else if( !stack.empty() ){
            nodes = stack.pop_back()->next;
        }
    }*/
}


//
class AddShipProcessor : public HttpPostProcessor
{
public:
    AddShipProcessor(const HttpRequest& request, ShipStorage* shipStorage );
    virtual ~AddShipProcessor();

    int IteratePostData(MHD_ValueKind kind, const char *key, const char *filename, const char *contentType, const char *transferEncoding, const char *data, uint64_t offset, size_t size);

    ShipStorage* m_shipStorage;
    int m_flagShaderSize;
    u8* m_flagShader;
    f32 m_shipPosX;
    f32 m_shipPosZ;
    f32 m_shipRotY;
    bool m_isHeadersValid;

protected:
    virtual void FinalizeRequest();
};


//
AddShipProcessor::AddShipProcessor( const HttpRequest& request, ShipStorage* shipStorage )
    : HttpPostProcessor( request )
    , m_shipStorage( shipStorage )
    , m_flagShader( nullptr )
    , m_flagShaderSize( 0 )
    , m_isHeadersValid( false )
{
    static std::string contentLengthKeyStr( "content-length" );
    static std::string posXKeyStr( "pos_x" );
    static std::string posZKeyStr( "pos_z" );
    static std::string rotYKeyStr( "rot_y" );
    int headerRead = 0;

    if( FindInMap( request.headers, contentLengthKeyStr, m_flagShaderSize ) ) {
        m_flagShader = new u8[ m_flagShaderSize ];
        headerRead++;
    }

    if( FindInMap( request.queryString, posXKeyStr, m_shipPosX ) )
        headerRead++;

    if( FindInMap( request.queryString, posZKeyStr, m_shipPosZ ) )
        headerRead++;

    if( FindInMap( request.queryString, rotYKeyStr, m_shipRotY ) )
        headerRead++;

    m_isHeadersValid = headerRead == 4;
}


//
AddShipProcessor::~AddShipProcessor() {
    delete[] m_flagShader;
}


//
void AddShipProcessor::FinalizeRequest() {
    if( !m_isHeadersValid ) {
        Complete( HttpResponse( MHD_HTTP_BAD_REQUEST ) );
        return;
    }

    if( !Shader::IsValidPixelShader( m_flagShader ) ) {
        Complete( HttpResponse( MHD_HTTP_BAD_REQUEST ) );
        return;
    }

    uuid id;
    uuid_generate( id.bytes );

    if( m_shipStorage->AddShip( id, m_shipPosX, m_shipPosZ, m_shipRotY, m_flagShader ) ) {
        char* uuidStr = ( char* )malloc( 64 );
        memset( uuidStr, 0, 64 );
        uuid_unparse( id.bytes, uuidStr );
        Complete( HttpResponse( MHD_HTTP_OK, uuidStr, strlen( uuidStr ), Headers() ) );
     } else
        Complete( HttpResponse(MHD_HTTP_BAD_REQUEST) );
}


//
int AddShipProcessor::IteratePostData( MHD_ValueKind kind, const char *key, const char *filename, const char *contentType,
                                       const char *transferEncoding, const char *data, uint64_t offset, size_t size ) {
    if( strncmp( key, "flag_shader", 11 ) == 0 && m_flagShader )
        memcpy( m_flagShader + offset, data, size );

    return MHD_YES;
}


//
class RequestHandler : public HttpRequestHandler
{
public:
    RequestHandler( ShipStorage* shipStorage, VertexBuffer* shipVb );

    HttpResponse HandleGet( HttpRequest request );
    HttpResponse HandlePost( HttpRequest request, HttpPostProcessor **postProcessor );

private:
    ShipStorage* m_shipStorage;
    VertexBuffer* m_shipVb;
};


//
RequestHandler::RequestHandler( ShipStorage* shipStorage, VertexBuffer* shipVb )
    : m_shipStorage( shipStorage )
    , m_shipVb( shipVb )
{
}


//
void png_to_mem(void *context, void *data, int size)
{
    HttpResponse* response = ( HttpResponse* )context;
    response->content = ( char* )malloc( size );
    memcpy( response->content, data, size );
    response->contentLength = size;
}


//
HttpResponse RequestHandler::HandleGet( HttpRequest request ) {
    if( ParseUrl( request.url, 1, "draw" ) )
    {
        static std::string camPosXStr( "pos_x" );
        static std::string camPosYStr( "pos_y" );
        static std::string camPosZStr( "pos_z" );
        static std::string camAimPosXStr( "aimpos_x" );
        static std::string camAimPosYStr( "aimpos_y" );
        static std::string camAimPosZStr( "aimpos_z" );

        Lib3dsVector camPos, camAt, camUp;
        camPos[ 0 ] = 0.0f;
        camPos[ 1 ] = 0.0f;
        camPos[ 2 ] = -10.0f;
        camAt[ 0 ] = 0.0f;
        camAt[ 1 ] = 0.0f;
        camAt[ 2 ] = 0.0f;
        //camUp[ 0 ] = 0.0f;
        //camUp[ 1 ] = 1.0f;
        //camUp[ 2 ] = 0.0f;

        FindInMap( request.queryString, camPosXStr, camPos[ 0 ] );
        FindInMap( request.queryString, camPosYStr, camPos[ 1 ] );
        FindInMap( request.queryString, camPosZStr, camPos[ 2 ] );
        FindInMap( request.queryString, camAimPosXStr, camAt[ 0 ] );
        FindInMap( request.queryString, camAimPosYStr, camAt[ 1 ] );
        FindInMap( request.queryString, camAimPosZStr, camAt[ 2 ] );

        // build camUp vector
        Lib3dsVector upVector, temp, dir;
        upVector[ 0 ] = 0.0f; upVector[ 1 ] = 1.0f; upVector[ 2 ] = 0.0f;
        lib3ds_vector_sub( dir, camAt, camPos );
        lib3ds_vector_normalize( dir );
        lib3ds_vector_cross( temp, dir, upVector );
        lib3ds_vector_cross( camUp, temp, dir );

        // draw
        Lib3dsMatrix view, proj, viewProj;
        BuildViewMatrix( view, camPos, camAt, camUp );
        BuildProjMatrix( proj, 90.0f / 180.0f * LIB3DS_PI, 1.0f, 0.1f, 100.0f );
        //BuildOrthoProjMatrix( proj, 4.0, 4.0, 0.1f, 100.0f );
        lib3ds_matrix_copy( viewProj, proj );
        lib3ds_matrix_mult( viewProj, view );
        lib3ds_matrix_transpose( viewProj );

        Image image( 512, 512 );
        Image depthRt( 512, 512 );
        Shader shipVs( "shaders/ship.vs.bin" );
        Shader shipPs( "shaders/ship.ps.bin" );

        PipelineState pState;
        memcpy( pState.constants, viewProj, 4 * 4 * sizeof( float ) );
        memcpy( &pState.constants[ 4 ], camPos, 4 * sizeof( float ) );
        pState.ib = nullptr;
        pState.rt = &image;
        pState.depthRt = &depthRt;

        ClearRenderTarget( pState.rt, 50, 50, 127, 255 );
        ClearDepthRenderTarget( pState.depthRt, 1.0f );

        const f32 MAX_DISTANCE = 100.0f;
        Ship* ship = m_shipStorage->GetListTail();
        while( ship ) {
            // simple visibility test
            Lib3dsVector shipPos, dir;
            shipPos[ 0 ] = ship->m_posX; shipPos[ 1 ] = 0.0f; shipPos[ 2 ] = ship->m_posZ;
            lib3ds_vector_sub( dir, shipPos, camPos );
            f32 distanceSqr = lib3ds_vector_squared( dir );
            if( distanceSqr > MAX_DISTANCE * MAX_DISTANCE ) {
                ship = ship->m_previousShip;
                continue;
            }

            // prepare world transform matrix
            Lib3dsMatrix tr, rot;
            lib3ds_matrix_identity( tr );
            lib3ds_matrix_identity( rot );
            lib3ds_matrix_rotate_y( rot, ship->m_rotY );
            lib3ds_matrix_translate( tr, shipPos );
            lib3ds_matrix_mult( tr, rot );
            lib3ds_matrix_transpose( tr );
            // set world transform matrix
            memcpy( &pState.constants[ 5 ], tr, 4 * 4 * sizeof( float ) );
            // draw ship
            pState.vb = m_shipVb;
            pState.vs = &shipVs;
            pState.ps = &shipPs;
            Draw( pState );
            // TODO draw flag

            ship = ship->m_previousShip;
        }

        Headers responseHeaders;
        responseHeaders.insert( { "Content-Type", "image/png" } );

        HttpResponse response;
        response.code = MHD_HTTP_OK;
        response.headers = responseHeaders;

        stbi_write_png_to_func( png_to_mem, &response, image.width, image.height, 4, image.rgba, image.width * sizeof( u32 ) );

        return response;
    }
    if( ParseUrl( request.url, 1, "get_shader" ) )
    {
        static std::string idKey( "id" );
        std::string idStr;
        if( !FindInMap( request.queryString, idKey, idStr ) )
            return HttpResponse( MHD_HTTP_BAD_REQUEST );

        uuid id;
        uuid_parse( idStr.c_str(), id.bytes );
        Ship* ship = m_shipStorage->GetShip( id );
        if( !ship )
            return HttpResponse( MHD_HTTP_NOT_FOUND );

        char* responseData = ( char* )malloc( ship->m_flagShader.GetSize() );
        char* copyDst = responseData;
        memcpy( copyDst, &ship->m_flagShader.header, sizeof( Shader::Header ) );
        copyDst += sizeof( Shader::Header );
        memcpy( copyDst, ship->m_flagShader.instructions, ship->m_flagShader.GetSize() -sizeof( Shader::Header ) );
        return HttpResponse( MHD_HTTP_OK, responseData, ship->m_flagShader.GetSize(), Headers() );
    }
    return HttpResponse( MHD_HTTP_NOT_FOUND );
}


//
HttpResponse RequestHandler::HandlePost( HttpRequest request, HttpPostProcessor **postProcessor ) {
    if( ParseUrl( request.url, 1, "add_ship" ) ) {
        *postProcessor = new AddShipProcessor( request, m_shipStorage );
        return HttpResponse();
    }

    return HttpResponse( MHD_HTTP_NOT_FOUND );
}


//
void GpuTests()
{
    DrawTest();
    TextureTest();

    timespec tp;
    double startTime, endTime;
    clock_gettime( CLOCK_REALTIME, &tp );
    startTime = tp.tv_sec + tp.tv_nsec / 1000000000.0;
    DrawShip();
    clock_gettime( CLOCK_REALTIME, &tp );
    endTime = tp.tv_sec + tp.tv_nsec / 1000000000.0;
    printf( ":: Time: %f\n", endTime - startTime );
}


//
void Service()
{
    VertexBuffer* shipVb = LoadShip();
    ShipStorage shipStorage( "storage.dat" );
    RequestHandler handler( &shipStorage, shipVb );
    HttpServer server(&handler);

    server.Start(16780);

    while(1){
        sleep(1);
    }

    server.Stop();
    delete shipVb;
}


int main()
{
    //GpuTests();
    Service();
    return 0;
}
