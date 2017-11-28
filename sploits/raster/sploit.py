#!/usr/bin/env python3
from __future__ import print_function
from sys import argv, stderr
import os
import requests
import json
import random
import string
import re
import io
from PIL import Image

guid_regex = re.compile( '^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}' )

##
def close(msg):
	print(msg)
	exit(1)


##
def add_ship( addr, bin_file ):
	pos_x = int( random.uniform( -1000000, 1000000 ) );
	pos_z = int( random.uniform( -1000000, 1000000 ) );
	rot_y = 0#random.uniform( 0, 3.1415926 );
	
	url = 'http://%s/add_ship?pos_x=%f&pos_z=%f&rot_y=%f' % ( addr, pos_x, pos_z, rot_y )
	print( url )
	files = { 'flag_shader': open( bin_file, 'rb' ).read() }
	try:
		r = requests.post(url, files=files )
		if r.status_code == 502:
			close("Service is down")
		if r.status_code != 200:
			close( "Invalid status code: %s %d" % ( url, r.status_code ) )	

		if not guid_regex.match( r.text ):
			close( "Invalid guid received" )
	except Exception as e:
		 close("HTTP error: %s" % e)

	return json.dumps( { 'x' : pos_x, 'z' : pos_z, 'ry' : rot_y } )


##
def draw( addr, pos_json ):
	params = json.loads( pos_json )

	pos_x = params[ 'x' ] + 0.4
	pos_y = 1.6
	pos_z = params[ 'z' ] - 0.3
	aimpos_x = pos_x
	aimpos_y = pos_y
	aimpos_z = params[ 'z' ]

	url = 'http://%s/draw?pos_x=%f&pos_y=%f&pos_z=%f&aimpos_x=%f&aimpos_y=%f&aimpos_z=%f' % ( addr, pos_x, pos_y, pos_z, aimpos_x, aimpos_y, aimpos_z )
	print( url )
	try:
		r = requests.get( url )
		if r.status_code == 502:
			close("Service is down")
		if r.status_code != 200:
			close( "Invalid status code: %s %d" % ( url, r.status_code ) )	
	except Exception as e:
		close("HTTP error: %s" % e)

	try:
		stream = io.BytesIO( r.content )
		img = Image.open( stream )

		if img.size[ 0 ] != 64 or img.size[ 0 ] != 64:
			close("Invalid image size %ux%u" % ( img.size[ 0 ], img.size[ 1 ] ) )			
		
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
		payload = []
		for iy in range( 0, 2 ):
			for ix in range( 0, 4 ):
				p = pixels[ int( x ), int( y ) ]
				payload.append( p );
				x += stepX
			y += stepY
			x = startX

		return payload

	except Exception as e:
		close("Invalid response: %s" % e)


##
def compile_shader( shader_source ):
	name = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8) )
	tmp_file = "/tmp/%s.ps" % name
	open( tmp_file, 'w' ).write( shader_source )

	bin_file = "/tmp/%s.ps.bin" % name
	cmd = "./compiler ps %s %s" % ( tmp_file, bin_file )
	os.system( cmd )
	os.remove( tmp_file )

	return bin_file


##
def compile_shader():
	source_file = "shader.ps"
	bin_file = "shader.ps.bin"

	cmd = "./compiler ps %s %s" % ( source_file, bin_file )
	os.system( cmd )

	return bin_file


##
addr = argv[ 1 ]#"127.0.0.1:16780"
bin_file = compile_shader()
flag_id = add_ship( addr, bin_file )
draw( addr, flag_id )
close("OK")
