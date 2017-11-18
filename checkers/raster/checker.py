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

	pos_x = random.uniform( -1000000, 1000000 );
	pos_z = random.uniform( -1000000, 1000000 );
	rot_y = random.uniform( 0, 3.1415926 );

	print( pos_x )
	print( pos_z )
	print( rot_y )

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

		print( r.text )

		if not guid_regex.match( r.text ):
			close( CORRUPT, "Service corrupted", "Invalid guid received" )

		try:
			flag_id = json.dumps( { 'id' : r.text } )
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

	bin_file = compile_shader( flag, id );

	url = 'http://%s/get_shader?id=%s' % ( addr, id )
	try:
		headers = { 'User-Agent' : UserAgents.get() }
		r = requests.get( url, headers=headers )
		if r.status_code == 502:
			close(DOWN, "Service is down", "Nginx 502", bin_file)
		if r.status_code != 200:
			close( MUMBLE, "Invalid HTTP response", "Invalid status code: %s %d" % ( url, r.status_code ), bin_file )	
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error: %s" % e, bin_file)

	if r.content != open( bin_file, 'rb' ).read():
		close( CORRUPT, "Service corrupted", "Flag does not match", bin_file )
	close( OK, fileToRemove=bin_file )


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
