#!/usr/bin/env python3
from __future__ import print_function
from sys import argv, stderr
import os
import requests
import UserAgents
import json
import random
import re
from struct import *
import hashlib
import time 
from PIL import Image
import io

SERVICE_NAME = "raster"
OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


guid_regex = re.compile( '^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}' )


def close(code, public="", private="", fileToRemove=""):
	if public:
		print(public)
	if private:
		print(private, file=stderr)
	if fileToRemove:
		os.remove( fileToRemove )
	print('Exit with code %d' % code, file=stderr)
	exit(code)


def check(*args):
	close(OK)

def compile_shader( flag, flag_id ):
	intro = ""
	regIdx = 0
	for i in range( 0, 32, 4 ):
		b0 = ord( flag[ i + 0: i + 1 ] )
		b1 = ord( flag[ i + 1: i + 2 ] )
		b2 = ord( flag[ i + 2: i + 3 ] )
		b3 = ord( flag[ i + 3: i + 4 ] )
		intro = intro + "seti r%d.xyzw %d %d %d %d\n" % ( regIdx, b0, b1, b2, b3 )
		regIdx += 1

	shader_source = intro + open( "flag.ps", 'r' ).read()

	tmp_file = "/tmp/%s.ps" % flag_id
	bin_file = "/tmp/%s.ps.bin" % flag_id
	open( tmp_file, 'w' ).write( shader_source )

	cmd = "./compiler ps %s %s" % ( tmp_file, bin_file )
	os.system( cmd )
	os.remove( tmp_file )

	return bin_file

def put(*args):
	addr = args[0]
	flag_id = args[1]
	flag = args[2]

	pos_x = int( random.uniform( -1000000, 1000000 ) );
	pos_z = int( random.uniform( -1000000, 1000000 ) );
	rot_y = 0#random.uniform( 0, 3.1415926 );

	bin_file = compile_shader( flag, flag_id )
	
	flag_id = "" # reset flag id, we will build new, based on service response
	url = 'http://%s/add_ship?pos_x=%f&pos_z=%f&rot_y=%f' % ( addr, pos_x, pos_z, rot_y )
	files = { 'flag_shader': open( bin_file, 'rb' ).read() }
	headers = { 'User-Agent' : UserAgents.get() }
	try:
		r = requests.post(url, files=files, headers=headers )
		if r.status_code == 502:
			close(DOWN, "Service is down", "Nginx 502", bin_file)
		if r.status_code != 200:
			close( MUMBLE, "Submit error", "Invalid status code: %s %d" % ( url, r.status_code ), bin_file )	

		if not guid_regex.match( r.text ):
			close( CORRUPT, "Service corrupted", "Invalid guid received" )

		try:
			flag_id = json.dumps( { 'id' : r.text, 'x' : pos_x, 'z' : pos_z, 'ry' : rot_y } )
		except Exception as e:
			close(CORRUPT, "Service corrupted", "Service returns invalid guid: %s" % e, bin_file)			
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error: %s" % e, fileToRemove=bin_file)
	close(OK, flag_id, fileToRemove=bin_file)
	

def get(*args):
	addr = args[0]
	flag_id = args[1]
	flag = args[2]
	params = json.loads( flag_id )

	id = params[ 'id' ]
	pos_x = params[ 'x' ] + 0.4
	pos_y = 1.6
	pos_z = params[ 'z' ] - 0.3
	aimpos_x = pos_x
	aimpos_y = pos_y
	aimpos_z = params[ 'z' ]

	url = 'http://%s/draw?pos_x=%f&pos_y=%f&pos_z=%f&aimpos_x=%f&aimpos_y=%f&aimpos_z=%f' % ( addr, pos_x, pos_y, pos_z, aimpos_x, aimpos_y, aimpos_z )
	#print( url )
	try:
		headers = { 'User-Agent' : UserAgents.get() }
		r = requests.get( url, headers=headers )
		if r.status_code == 502:
			close(DOWN, "Service is down", "Nginx 502", bin_file)
		if r.status_code != 200:
			close( MUMBLE, "Invalid HTTP response", "Invalid status code: %s %d" % ( url, r.status_code ), bin_file )	
	except Exception as e:
		close(DOWN, "HTTP Error", "HTTP error: %s" % e, bin_file)

	try:
		stream = io.BytesIO( r.content )
		img = Image.open( stream )

		if img.size[ 0 ] != 64 or img.size[ 0 ] != 64:
			close(CORRUPT, "Service corrupted", "Invalid image size %ux%u" % ( img.size[ 0 ], img.size[ 1 ] ) )			
		
		left = -1
		right = -1
		pixels = img.load()
		RED = ( 255, 0, 0, 255 )

		for y in range( 1, 63 ):
			for x in range( 1, 63 ):
				if pixels[ x, y ] != RED and pixels[ x + 1, y ] == RED and left == -1:
					#print( "left", x, y, pixels[ x, y ], pixels[ x + 1, y ] )
					left = x
				if pixels[ x, y ] == RED and pixels[ x + 1, y ] != RED and right == -1:
					#print( "right", x, y, pixels[ x, y ], pixels[ x + 1, y ] )
					right = x

		top = -1
		bottom = -1
		for x in range( 1, 63 ):
			for y in range( 1, 63 ):
				if pixels[ x, y ] != RED and pixels[ x, y + 1 ] == RED and top == -1:
					#print( "top", x, y, pixels[ x, y ], pixels[ x, y + 1 ] )
					top = y
				if pixels[ x, y ] == RED and pixels[ x, y + 1 ] != RED and bottom == -1:
					#print( "bottom", x, y, pixels[ x, y ], pixels[ x, y + 1 ] )
					bottom = y

		width = right - left
		height = bottom - top
		stepX = width / 6
		stepY = height / 4
		
		startX = left + stepX * 1.5
		startY = top + stepY * 1.5

		x = startX
		y = startY
		restored_flag = ""
		for iy in range( 0, 2 ):
			for ix in range( 0, 4 ):
				p = pixels[ int( x ), int( y ) ]
				restored_flag += chr( p[ 0 ] ) + chr( p[ 1 ] ) + chr( p[ 2 ] ) + chr( p[ 3 ] )
				x += stepX
			y += stepY
			x = startX

		if restored_flag != flag:
			close(CORRUPT, "Service corrupted", "Invalid flag: %s" % restored_flag )
	except Exception as e:
		close(DOWN, "Service corrupted", "Invalid response: %s" % e)

	close( OK )


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


if __name__ == '__main__':
	try:
		COMMANDS.get(argv[1], not_found)(*argv[2:])
	except Exception as e:
		close(CHECKER_ERROR, "Evil checker", "INTERNAL ERROR: %s" % e)
