#pragma once
#include "gpu.h"
#include <stdio.h>
#include <stdint.h>
#include <pthread.h>
#include <uuid/uuid.h>


//
struct uuid
{
    uuid_t bytes;
};


//
class Ship
{
public:
    Ship( uuid name, float posX, float posZ, float rotY, const u8* shader, Ship *previousShip );
    virtual ~Ship();

    uuid m_name;
    float m_posX;
    float m_posZ;
    float m_rotY;
    Shader m_flagShader;

    Ship* m_previousShip;
};


//
class ShipStorage
{
public:
    ShipStorage(const char *path);
    virtual ~ShipStorage();
	
    Ship *GetShip(uuid name);
    bool AddShip( uuid name, float posX, float posZ, float rotY, const u8* shader );
    //uuid *ListShips(int *count);
    Ship* GetListTail() { return m_ships; }

private:
    Ship* m_ships;
    int m_shipsCount;

    FILE* m_backingFile;

    pthread_mutex_t m_sync = PTHREAD_MUTEX_INITIALIZER;

    Ship* AddShipInternal( uuid name, float posX, float posZ, float rotY, const u8* shader );
};
