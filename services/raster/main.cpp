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
#include <tuple>


//
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


//
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
    delete[] normalL;

    return vb;
}


//
std::tuple< VertexBuffer*, IndexBuffer* > CreateFlagVb()
{
    f32 left = 0.1;
    f32 right = 0.6f;
    f32 bottom = 1.5f;
    f32 top = 1.8f;
    f32 z = 0.1f;

    VertexBuffer* vb = new VertexBuffer( 8, 2 );
    // front
    vb->vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,    bottom,left );
    vb->vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 1.0f,  0.0f );

    vb->vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,    top,   left );
    vb->vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 0.0f,  0.0f );

    vb->vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,    top,   right);
    vb->vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 0.0f,  1.0f );

    vb->vertices[ 3 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,    bottom,right );
    vb->vertices[ 3 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 1.0f,  1.0f );
    // back
    vb->vertices[ 4 * 2 + 0 ].f = _mm_set_ps( 1.0f, -z,   bottom,right );
    vb->vertices[ 4 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 1.0f,  0.0f );

    vb->vertices[ 5 * 2 + 0 ].f = _mm_set_ps( 1.0f, -z,   top,   right );
    vb->vertices[ 5 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 0.0f,  0.0f );

    vb->vertices[ 6 * 2 + 0 ].f = _mm_set_ps( 1.0f, -z,   top,   left);
    vb->vertices[ 6 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 0.0f,  1.0f );

    vb->vertices[ 7 * 2 + 0 ].f = _mm_set_ps( 1.0f, -z,   bottom,left );
    vb->vertices[ 7 * 2 + 1 ].f = _mm_set_ps( 1.0f, 0.0f, 1.0f,  1.0f );

    IndexBuffer* ib = new IndexBuffer( 12 );
    ib->indices[ 0 ] = 0;
    ib->indices[ 1 ] = 1;
    ib->indices[ 2 ] = 2;
    ib->indices[ 3 ] = 0;
    ib->indices[ 4 ] = 2;
    ib->indices[ 5 ] = 3;
    // back
    ib->indices[ 6 ] = 4;
    ib->indices[ 7 ] = 5;
    ib->indices[ 8 ] = 6;
    ib->indices[ 9 ] = 4;
    ib->indices[ 10 ] = 6;
    ib->indices[ 11 ] = 7;

    return std::make_tuple( vb, ib );
}


//
VertexBuffer* CreateSkyVb()
{
    VertexBuffer* vb = new VertexBuffer( 6, 2 );
    float z = 1.0f;
    vb->vertices[ 0 * 2 + 0 ].f = _mm_set_ps( 1.0f, z, -1.0f,  -1.0f );
    vb->vertices[ 0 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  0.0f );

    vb->vertices[ 1 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,  1.0f, -1.0f );
    vb->vertices[ 1 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  0.0f );

    vb->vertices[ 2 * 2 + 0 ].f = _mm_set_ps( 1.0f, z,  1.0f,  1.0f );
    vb->vertices[ 2 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  0.0f,  1.0f );

    vb->vertices[ 3 * 2 + 0 ].f = vb->vertices[ 0 * 2 + 0 ].f;
    vb->vertices[ 3 * 2 + 1 ].f = vb->vertices[ 0 * 2 + 1 ].f;

    vb->vertices[ 4 * 2 + 0 ].f = vb->vertices[ 2 * 2 + 0 ].f;
    vb->vertices[ 4 * 2 + 1 ].f = vb->vertices[ 2 * 2 + 1 ].f;

    vb->vertices[ 5 * 2 + 0 ].f = _mm_set_ps( 1.0f, z, -1.0f,  1.0f );
    vb->vertices[ 5 * 2 + 1 ].f = _mm_set_ps( 0.0f, 0.0f,  1.0f,  1.0f );

    return vb;
}


//
bool CheckIntersection( Lib3dsVector planePos, Lib3dsVector rayStart, Lib3dsVector rayDir, f32&d )
{
    if( fabs( rayDir[ 1 ] ) < 1e-05 )
        return false;

    d = ( planePos[ 1 ] - rayStart[ 1 ] ) / rayDir[ 1 ];
    return d >= 0.0f && d <= 1.0f;
}


//
bool BuildSeaVb( VertexBuffer* vb, Lib3dsMatrix view, Lib3dsMatrix proj, f32 nearPlane, f32 farPlane, Lib3dsVector offset )
{
    if( offset[ 1 ] < 0.0f )
        return false;

    f32 sx = proj[ 0 ][ 0 ];
    f32 sy = proj[ 1 ][ 1 ];
    //
    // 1______2
    // |\ __/ |
    // | |__| |
    // |/___\_|
    // 0      3
    //
    Lib3dsVector nearPoints[ 4 ];
    nearPoints[ 0 ][ 0 ] = -1.0f * nearPlane / sx; nearPoints[ 0 ][ 1 ] = -1.0f * nearPlane / sy; nearPoints[ 0 ][ 2 ] = nearPlane;
    nearPoints[ 1 ][ 0 ] = -1.0f * nearPlane / sx; nearPoints[ 1 ][ 1 ] =  1.0f * nearPlane / sy; nearPoints[ 1 ][ 2 ] = nearPlane;
    nearPoints[ 2 ][ 0 ] =  1.0f * nearPlane / sx; nearPoints[ 2 ][ 1 ] =  1.0f * nearPlane / sy; nearPoints[ 2 ][ 2 ] = nearPlane;
    nearPoints[ 3 ][ 0 ] =  1.0f * nearPlane / sx; nearPoints[ 3 ][ 1 ] = -1.0f * nearPlane / sy; nearPoints[ 3 ][ 2 ] = nearPlane;

    Lib3dsVector farPoints[ 4 ];
    farPoints[ 0 ][ 0 ] = -1.0f * farPlane / sx; farPoints[ 0 ][ 1 ] = -1.0f * farPlane / sy; farPoints[ 0 ][ 2 ] = farPlane;
    farPoints[ 1 ][ 0 ] = -1.0f * farPlane / sx; farPoints[ 1 ][ 1 ] =  1.0f * farPlane / sy; farPoints[ 1 ][ 2 ] = farPlane;
    farPoints[ 2 ][ 0 ] =  1.0f * farPlane / sx; farPoints[ 2 ][ 1 ] =  1.0f * farPlane / sy; farPoints[ 2 ][ 2 ] = farPlane;
    farPoints[ 3 ][ 0 ] =  1.0f * farPlane / sx; farPoints[ 3 ][ 1 ] = -1.0f * farPlane / sy; farPoints[ 3 ][ 2 ] = farPlane;

    Lib3dsVector viewPos;
    viewPos[ 0 ] = view[ 3 ][ 0 ]; viewPos[ 1 ] = view[ 3 ][ 1 ]; viewPos[ 2 ] = view[ 3 ][ 2 ];
    Lib3dsMatrix viewInv;
    for( u32 i = 0; i < 3; i++ )
        for( u32 j = 0; j < 3; j++ ) {
            viewInv[ i ][ j ] = view[ j ][ i ];
        }
    viewInv[ 0 ][ 3 ] = 0.0f; viewInv[ 1 ][ 3 ] = 0.0f; viewInv[ 2 ][ 3 ] = 0.0f;
    viewInv[ 3 ][ 0 ] = 0.0f; viewInv[ 3 ][ 1 ] = 0.0f; viewInv[ 3 ][ 2 ] = 0.0f; viewInv[ 3 ][ 3 ] = 1.0f;

    Lib3dsVector nearPointsWS[ 4 ];
    Lib3dsVector farPointsWS[ 4 ];
    for( u32 i = 0; i < 4; i++ ) {
        lib3ds_vector_transform( nearPointsWS[ i ], viewInv, nearPoints[ i ] );
        lib3ds_vector_sub( nearPointsWS[ i ], nearPointsWS[ i ], viewPos );

        lib3ds_vector_transform( farPointsWS[ i ], viewInv, farPoints[ i ] );
        lib3ds_vector_sub( farPointsWS[ i ], farPointsWS[ i ], viewPos );
    }

    //
    Lib3dsVector seaPos;
    lib3ds_vector_zero( seaPos );
    seaPos[ 1 ] = -offset[ 1 ];

    //
    Lib3dsVector intersections[ 4 ];
    u32 mask = 0;

    for( u32 i = 0; i < 4; i++ ) {
        Lib3dsVector ray;
        lib3ds_vector_sub( ray, farPointsWS[ i ], nearPointsWS[ i ] );

        f32 d = 0.0f;
        if( CheckIntersection( seaPos, nearPointsWS[ i ], ray, d ) ) {
            lib3ds_vector_scalar( ray, d );
            lib3ds_vector_add( ray, nearPointsWS[ i ], ray );

            mask |= 1 << i;
            lib3ds_vector_copy( intersections[ i ], ray );
        }
    }

    if( mask != 0b1111 ) {
        Lib3dsVector rays[ 4 ];
        lib3ds_vector_sub( rays[ 0 ], nearPointsWS[ 1 ], nearPointsWS[ 0 ] );
        lib3ds_vector_sub( rays[ 3 ], nearPointsWS[ 2 ], nearPointsWS[ 3 ] );
        lib3ds_vector_sub( rays[ 1 ], farPointsWS[ 1 ], farPointsWS[ 0 ] );
        lib3ds_vector_sub( rays[ 2 ], farPointsWS[ 2 ], farPointsWS[ 3 ] );
        Lib3dsVector p0[ 4 ];
        lib3ds_vector_copy( p0[ 0 ], nearPointsWS[ 0 ] );
        lib3ds_vector_copy( p0[ 3 ], nearPointsWS[ 3 ] );
        lib3ds_vector_copy( p0[ 1 ], farPointsWS[ 0 ] );
        lib3ds_vector_copy( p0[ 2 ], farPointsWS[ 3 ] );

        for( u32 i = 0; i < 4; i++ ) {
            f32 d = 0.0f;
            if( CheckIntersection( seaPos, p0[ i ], rays[ i ], d ) ) {
                Lib3dsVector p;
                lib3ds_vector_copy( p, rays[ i ] );
                lib3ds_vector_scalar( p, d );
                lib3ds_vector_add( p, p0[ i ], p );

                u32 _mask = 1 << i;
                if( mask & _mask )
                    return false;
                mask |= _mask;
                lib3ds_vector_copy( intersections[ i ], p );
            }
        }
    }

    if( mask == 0 )
        return false;

    if( mask != 0b1111 )
        return false;

    vb->vertices[ 0 ].f = _mm_set_ps( 1.0f, intersections[ 0 ][ 2 ], intersections[ 0 ][ 1 ], intersections[ 0 ][ 0 ] );
    vb->vertices[ 1 ].f = _mm_set_ps( 1.0f, intersections[ 1 ][ 2 ], intersections[ 1 ][ 1 ], intersections[ 1 ][ 0 ] );
    vb->vertices[ 2 ].f = _mm_set_ps( 1.0f, intersections[ 2 ][ 2 ], intersections[ 2 ][ 1 ], intersections[ 2 ][ 0 ] );
    vb->vertices[ 3 ].f = vb->vertices[ 0 ].f;
    vb->vertices[ 4 ].f = vb->vertices[ 2 ].f;
    vb->vertices[ 5 ].f = _mm_set_ps( 1.0f, intersections[ 3 ][ 2 ], intersections[ 3 ][ 1 ], intersections[ 3 ][ 0 ] );

    return true;
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
		printf( "Invalid query\n" );
        return;
    }

    if( !Shader::IsValidPixelShader( m_flagShader ) ) {
        Complete( HttpResponse( MHD_HTTP_BAD_REQUEST ) );
		printf( "Invalid shader\n" );
        return;
    }

    uuid id;
    uuid_generate( id.bytes );

    if( m_shipStorage->AddShip( id, m_shipPosX, m_shipPosZ, m_shipRotY, m_flagShader ) ) {
        char* uuidStr = ( char* )malloc( 64 );
        memset( uuidStr, 0, 64 );
        uuid_unparse( id.bytes, uuidStr );
        Complete( HttpResponse( MHD_HTTP_OK, uuidStr, strlen( uuidStr ), Headers() ) );
		printf( "Ship added\n" );
     } else {
        Complete( HttpResponse(MHD_HTTP_BAD_REQUEST) );
		printf( "Failed to add ship \n" );
	 }
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
    RequestHandler( ShipStorage* shipStorage, VertexBuffer* shipVb, VertexBuffer* flagVb, IndexBuffer* flagIb, Image* skyTexture, Image* seaTexture, VertexBuffer* skyVb,
                    Shader* shipVs, Shader* shipPs, Shader* skyVs, Shader* skyPs, Shader* seaVs, Shader* seaPs );

    HttpResponse HandleGet( HttpRequest request );
    HttpResponse HandlePost( HttpRequest request, HttpPostProcessor **postProcessor );

private:
    ShipStorage* m_shipStorage;
    VertexBuffer* m_shipVb;
    VertexBuffer* m_flagVb;
    IndexBuffer* m_flagIb;
    Image* m_skyTexture;
    Image* m_seaTexture;
    VertexBuffer* m_skyVb;
    VertexBuffer* m_seaVb;
    Shader* m_shipVs;
    Shader* m_shipPs;
    Shader* m_skyVs;
    Shader* m_skyPs;
    Shader* m_seaVs;
    Shader* m_seaPs;
};


//
RequestHandler::RequestHandler(ShipStorage* shipStorage, VertexBuffer* shipVb, VertexBuffer* flagVb, IndexBuffer* flagIb, Image* skyTexture, Image* seaTexture, VertexBuffer* skyVb,
                               Shader* shipVs, Shader* shipPs, Shader* skyVs, Shader* skyPs, Shader* seaVs, Shader* seaPs )
    : m_shipStorage( shipStorage )
    , m_shipVb( shipVb )
    , m_flagVb( flagVb )
    , m_flagIb( flagIb )
    , m_seaTexture( seaTexture )
    , m_skyTexture( skyTexture )
    , m_skyVb( skyVb )
    , m_shipVs( shipVs )
    , m_shipPs( shipPs )
    , m_skyVs( skyVs )
    , m_skyPs( skyPs )
    , m_seaVs( seaVs )
    , m_seaPs( seaPs )
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
		
		// move to origin to improve precision
		Lib3dsVector offset;
		offset[ 0 ]= camPos[ 0 ]; offset[ 1 ]= camPos[ 1 ]; offset[ 2 ]= camPos[ 2 ];
		lib3ds_vector_sub( camPos, camPos, offset );
		lib3ds_vector_sub( camAt, camAt, offset );
		
        // build camUp vector
        Lib3dsVector upVector, temp, dir;
        upVector[ 0 ] = 0.0f; upVector[ 1 ] = 1.0f; upVector[ 2 ] = 0.0f;
        lib3ds_vector_sub( dir, camAt, camPos );
        lib3ds_vector_normalize( dir );
        lib3ds_vector_cross( temp, dir, upVector );
        lib3ds_vector_cross( camUp, temp, dir );

        // draw
        const f32 nearPlane = 0.1f;
        const f32 farPlane = 100.0f;
        Lib3dsMatrix view, proj, viewProj;
        BuildViewMatrix( view, camPos, camAt, camUp );
        BuildProjMatrix( proj, 90.0f / 180.0f * LIB3DS_PI, 1.0f, nearPlane, farPlane );
        //BuildOrthoProjMatrix( proj, 4.0, 4.0, 0.1f, 100.0f );
        lib3ds_matrix_copy( viewProj, proj );
        lib3ds_matrix_mult( viewProj, view );
        lib3ds_matrix_transpose( viewProj );

        const u32 S = 128;
        Image image( S, S );
        Image depthRt( S, S );

        PipelineState pState;
        memcpy( pState.constants, viewProj, 4 * 4 * sizeof( float ) );
        memcpy( &pState.constants[ 4 ], camPos, 4 * sizeof( float ) );
        pState.ib = nullptr;
        pState.rt = &image;
        pState.depthRt = &depthRt;

        ClearDepthRenderTarget( pState.depthRt, 1.0f );

        // draw sea
        VertexBuffer seaVb( 6, 1 );
        if( BuildSeaVb( &seaVb, view, proj, nearPlane + 0.5f, farPlane - 0.5f, offset ) ) {
            pState.vb = &seaVb;
            pState.textures[ 0 ] = m_seaTexture;
            pState.vs = m_seaVs;
            pState.ps = m_seaPs;
            Draw( pState );
        }

        // draw sky
        pState.vb = m_skyVb;
        pState.textures[ 0 ] = m_skyTexture;
        pState.vs = m_skyVs;
        pState.ps = m_skyPs;
        Draw( pState );

        // draw ships
        const f32 MAX_DISTANCE = 40.0f;
		const u32 MAX_SHIPS_TO_DRAW = 10;
		u32 shipsDrawn = 0;
        Ship* ship = m_shipStorage->GetListTail();
        while( ship ) {
			if( shipsDrawn >= MAX_SHIPS_TO_DRAW )
				break;
			
            // simple visibility test
            Lib3dsVector shipPos, dir;
            shipPos[ 0 ] = ship->m_posX; shipPos[ 1 ] = 0.0f; shipPos[ 2 ] = ship->m_posZ;
			lib3ds_vector_sub( shipPos, shipPos, offset ); // move to origin
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
            pState.vs = m_shipVs;
            pState.ps = m_shipPs;
            Draw( pState );
            // draw flag
            pState.vb = m_flagVb;
            pState.ib = m_flagIb;
            pState.ps = &ship->m_flagShader;
            Draw( pState );

            ship = ship->m_previousShip;			
			shipsDrawn++;
        }

        Headers responseHeaders;
        responseHeaders.insert( { "Content-Type", "image/png" } );

        HttpResponse response;
        response.code = MHD_HTTP_OK;
        response.headers = responseHeaders;

        stbi_write_png_to_func( png_to_mem, &response, image.width, image.height, 4, image.rgba, image.width * sizeof( u32 ) );

        return response;
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
void Service()
{
    VertexBuffer* shipVb = LoadShip();
    VertexBuffer* flagVb;
    IndexBuffer* flagIb;
    std::tie( flagVb, flagIb ) = CreateFlagVb();
    Image skyTexture;
    read_png( "textures/sky.png", skyTexture );
    Image seaTexture;
    read_png( "textures/water.png", seaTexture );
    VertexBuffer* skyVb = CreateSkyVb();
    Shader shipVs( "shaders/ship.vs.bin" );
    Shader shipPs( "shaders/ship.ps.bin" );
    Shader skyVs( "shaders/simple.vs.bin" );
    Shader skyPs( "shaders/texture.ps.bin" );
    Shader seaVs( "shaders/sea.vs.bin" );
    Shader seaPs( "shaders/sea.ps.bin" );

    ShipStorage shipStorage( "storage.dat" );
    RequestHandler handler( &shipStorage, shipVb, flagVb, flagIb, &skyTexture, &seaTexture, skyVb, &shipVs, &shipPs, &skyVs, &skyPs, &seaVs, &seaPs );
    HttpServer server(&handler);

    server.Start(16780);

    while(1)
        sleep(1);

    server.Stop();
    delete shipVb;
    delete flagVb;
    delete flagIb;
    delete skyVb;
}


int main()
{
    Service();
    return 0;
}
