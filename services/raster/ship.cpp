#include "ship.h"

#include <stdlib.h>
#include <string.h>


//
struct ShipHeader
{
    uuid name;
    f32 posX;
    f32 posZ;
    f32 rotY;
    i32 shaderSize;
};


Ship::Ship( uuid name, float posX, float posZ, float rotY, const u8* shader, Ship *previousShip )
    : m_name( name ), m_posX( posX ), m_posZ( posZ ), m_rotY( rotY ), m_flagShader( shader ), m_previousShip( previousShip )
{

}

Ship::~Ship()
{
}


ShipStorage::ShipStorage( const char* path )
{
    m_ships = NULL;
    m_shipsCount = 0;

    m_backingFile = fopen( path, "a+b" );

    if( !m_backingFile )
	{
        printf( "Failed to open storage file\n" );
        exit( 1 );
	}

    fseek( m_backingFile, 0, SEEK_SET );

    ShipHeader header;
    while( true )
	{
        if( fread( &header, sizeof( header ), 1, m_backingFile ) != 1 )
			break;

        u8* shader = new u8[ header.shaderSize ];
        fread( shader, 1, header.shaderSize, m_backingFile );

        AddShipInternal( header.name, header.posX, header.posZ, header.rotY, shader );

        delete[] shader;
	}
}

ShipStorage::~ShipStorage()
{
    for( Ship *d = m_ships; d != NULL; )
	{
        Ship *prev = d->m_previousShip;
		delete d;
		d = prev;
	}

    fclose( m_backingFile );
}

bool ShipStorage::AddShip( uuid name, float posX, float posZ, float rotY, const u8 *shader )
{
    pthread_mutex_lock( &m_sync );

    Ship* ship = AddShipInternal( name, posX, posZ, rotY, shader );
    if( ship ){
        ShipHeader header;

        header.name = name;
        header.posX = posX;
        header.posZ = posZ;
        header.rotY = rotY;
        header.shaderSize = ship->m_flagShader.GetSize();

        fwrite( &header, sizeof( header ), 1, m_backingFile);
        fwrite( shader, 1, header.shaderSize, m_backingFile );
        fflush( m_backingFile );
	}

    pthread_mutex_unlock( &m_sync );

    return ship != nullptr;
}

Ship* ShipStorage::AddShipInternal( uuid name,float posX, float posZ, float rotY, const u8* shader )
{
    Ship* d = new Ship( name, posX, posZ, rotY, shader, m_ships );

    m_ships = d;
    m_shipsCount++;

    return d;
}

/*uuid *ShipStorage::ListShips(int *count)
{
	*count = detectorCount;

	uuid *list = new uuid[*count];

	int i = 0;
    for (Ship *d = detectors; d != NULL; d = d->previousShip)
	{
		if (i >= *count)
			break;

		list[i++] = d->name;
	}

	return list;
}*/

Ship *ShipStorage::GetShip(uuid name)
{
    for( Ship* d = m_ships; d != NULL; d = d->m_previousShip )
	{
        if( !memcmp( &name, &d->m_name, sizeof( name ) ) )
			return d;
	}

	return NULL;
}
