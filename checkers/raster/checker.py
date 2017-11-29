#!/usr/bin/env python3
from __future__ import print_function
from sys import argv, stderr
import os
import requests
import UserAgents
import json
import random
import string
import re
from PIL import Image
import io

SERVICE_NAME = "raster"
OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


guid_regex = re.compile( '^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}' )
INST_LIST = [ "add", "addi", "sub", "subi", "mul", "muli", "div", "dot", "or", "and", "xor" ]
REG_LIST = [ "c", "r" ]
C_LIST = [ 'x', 'y', 'z', 'w' ]

CHECKS = [
	( ( "set r0.xy 6.0 2.0\n"		#set, add, sub, mul, div, cvtfi
		"add r1.x r0.x r0.y\n"
		"sub r1.y r0.x r0.y\n"
		"mul r1.z r0.x r0.y\n"
		"div r1.w r0.x r0.y\n"
		"cvtfi o0.xyzw r1.xyzw\n"
	), ( 8, 4, 12, 3 ) ),
	( ( "seti r0.xy 6 2\n"		#seti, addi, subi, muli, divi
		"addi r1.x r0.x r0.y\n"
		"subi r1.y r0.x r0.y\n"
		"muli r1.z r0.x r0.y\n"
		"divi r1.w r0.x r0.y\n"
		"mov o0.xyzw r1.xyzw\n"
	), ( 8, 4, 12, 3 ) ),
	( ( "set r0.xyz 2.0 4.0 4.0\n" #length, normalize, abs
		"length r1.x r0.xyz\n"
		"set r0.xyz 4.0 4.0 -2.0\n"
		"normalize r1.y r0.x\n"
		"normalize r1.z r0.y\n"
		"abs r1.w r0.z\n"
		"cvtfi o0.xyzw r1.xyzw\n"
	), ( 6, 1, 1, 2 ) ),
	( ( "set r0.xyz -1.0 2.0 0.5\n" #saturare, cvtif
		"saturate r1.xyz r0.xyz\n"
		"seti r0.w 10\n"
		"cvtif r1.w r0.w\n"
		"cvtfi o0.xyzw r1.xyzw\n"
	), ( 0, 1, 0, 10 ) ),
	( ( "set r0.xy 2.0 2.0\n" #cmpeq, ret
		"seti r1.xy 255 0\n"
		"cmpeq r0.x r0.y\n"
		"jmp_false 3\n"
		"mov o0.xyzw r1.xxxx\n"
		"ret\n"
		"mov o0.xyzw r1.yyyy\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "set r0.xy 2.0 3.0" #cmplt
		"seti r1.xy 255 0\n"
		"cmplt r0.x r0.y\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "set r0.xyzw 2.0 3.0 4.0 4.0\n" #cmple
		"seti r1.xy 255 0\n"
		"cmple r0.xz r0.yw\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "set r0.xy 3.0 2.0\n" #cmpgt
		"seti r1.xy 255 0\n"
		"cmpgt r0.x r0.y\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "set r0.xyzw 3.0 2.0 4.0 4.0\n" #cmpge
		"seti r1.xy 255 0\n"
		"cmpge r0.xz r0.yw\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "seti r0.xy 2 2\n" #cmpeqi
		"seti r1.xy 255 0\n"
		"cmpeqi r0.x r0.y\n"
		"jmp_false 3\n"
		"mov o0.xyzw r1.xxxx\n"
		"ret\n"
		"mov o0.xyzw r1.yyyy\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "seti r0.xy 2 3\n" #cmplti
		"seti r1.xy 255 0\n"
		"cmplti r0.x r0.y\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "seti r0.xy 3 2\n" #cmpgti
		"seti r1.xy 255 0\n"
		"cmpgti r0.x r0.y\n"
		"jmp_true 3\n"
		"mov o0.xyzw r1.yyyy\n"
		"ret\n"
		"mov o0.xyzw r1.xxxx\n"
	), ( 255, 255, 255, 255 ) ),
	( ( "seti r0.xyzw 4 8 14 7\n" # or, and, xor, shl, shr
		"or o0.x r0.x r0.y\n" # 4 | 8 = 12
		"and o0.y r0.z r0.w\n" # 14 & 7 = 6
		"seti r0.xy 14 7\n"
		"xor o0.z r0.x r0.y\n" # 14 ^ 7 = 9
		"seti r0.xyz 6 1 2\n" 
		"shr o0.w r0.x r0.y\n" # 6 >> 1 = 3
		"shl o0.w o0.w r0.z\n" # 3 << 2 = 12
	), ( 12, 6, 9, 12 ))
]


def close(code, public="", private="", fileToRemove=""):
	if public:
		print(public)
	if private:
		print(private, file=stderr)
	if fileToRemove:
		os.remove( fileToRemove )
	print('Exit with code %d' % code, file=stderr)
	exit(code)


##
def add_ship( addr, bin_file ):
	pos_x = int( random.uniform( -1000000, 1000000 ) );
	pos_z = int( random.uniform( -1000000, 1000000 ) );
	rot_y = 0#random.uniform( 0, 3.1415926 );
	
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
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error: %s" % e, fileToRemove=bin_file)

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
	#print( url )
	try:
		headers = { 'User-Agent' : UserAgents.get() }
		r = requests.get( url, headers=headers )
		if r.status_code == 502:
			close(DOWN, "Service is down", "Nginx 502")
		if r.status_code != 200:
			close( MUMBLE, "Invalid HTTP response", "Invalid status code: %s %d" % ( url, r.status_code ) )	
	except Exception as e:
		close(DOWN, "HTTP Error", "HTTP error: %s" % e)

	try:
		stream = io.BytesIO( r.content )
		img = Image.open( stream )

		if img.size[ 0 ] != 128 or img.size[ 0 ] != 128:
			close(CORRUPT, "Service corrupted", "Invalid image size %ux%u" % ( img.size[ 0 ], img.size[ 1 ] ) )			
		
		left = -1
		right = -1
		pixels = img.load()
		RED = ( 255, 0, 0, 255 )

		for y in range( 1, 127 ):
			for x in range( 1, 127 ):
				if pixels[ x, y ] != RED and pixels[ x + 1, y ] == RED and left == -1:
					#print( "left", x, y, pixels[ x, y ], pixels[ x + 1, y ] )
					left = x
				if pixels[ x, y ] == RED and pixels[ x + 1, y ] != RED and right == -1:
					#print( "right", x, y, pixels[ x, y ], pixels[ x + 1, y ] )
					right = x

		top = -1
		bottom = -1
		for x in range( 1, 127 ):
			for y in range( 1, 127 ):
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
		close(DOWN, "Service corrupted", "Invalid response: %s" % e)


##
def gen_swizzle( size ):
	swizzle = "."
	for i in range( 0, size ):
		j = random.randint( 0, len( C_LIST ) - 1 )
		swizzle += C_LIST[ j ]
	return swizzle


## 
def gen_random_shader():
	inst_num = random.randint( 2, 10 )
	shader = ""
	for x in range( 0, inst_num ):
		i = random.randint( 0, len( INST_LIST ) - 1 )
		dstRi = random.randint( 0, 16 )
		src0R = random.randint( 0, len( REG_LIST ) - 1 )
		src0Ri = random.randint( 0, 16 )
		src1R = random.randint( 0, len( REG_LIST ) - 1 )
		src1Ri = random.randint( 0, 16 )
		swizzleSize = random.randint( 1, 4 )
		shader += INST_LIST[ i ] + " "
		shader += "r" + str( dstRi ) + gen_swizzle( swizzleSize ) + " "
		shader += REG_LIST[ src0R ] + str( src0Ri ) + gen_swizzle( swizzleSize ) + " "
		shader += REG_LIST[ src1R ] + str( src1Ri ) + gen_swizzle( swizzleSize ) + "\n"
	return shader


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
def check(*args):
	addr = args[0]
	
	c = random.randint( 0, len( CHECKS ) - 1 )
	shader = CHECKS[ c ][ 0 ]
	shader = open( "check.ps", 'r' ).read() + shader

	pre_shader = gen_random_shader()
	post_shader = gen_random_shader()
	shader = pre_shader + shader + post_shader
	#print( shader )
	
	bin_file = compile_shader( shader )
	pos = add_ship( addr, bin_file )
	payload = draw( addr, pos )

	# check payload
	for p in payload:
		cp = CHECKS[ c ][ 1 ]
		if p != cp:
			# checked
			close(CORRUPT, "Service corrupted", "Invalid paylod expected ( %u, %u, %u, %u ), received ( %u %u %u %u )" % ( cp[0], cp[1], cp[2], cp[3], p[0], p[1], p[2], p[3] ) )

	close( OK, fileToRemove=bin_file )


##
def compile_flag_shader( flag, flag_id ):
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


##
def put(*args):
	addr = args[ 0 ]
	flag_id = args[ 1 ]
	flag = args[ 2 ]
	bin_file = compile_flag_shader( flag, flag_id )
	flag_id = add_ship( addr, bin_file )
	close(OK, flag_id, fileToRemove=bin_file)


##
def get(*args):
	addr = args[0]
	flag_id = args[1]
	flag = args[2]

	payload = draw( addr, flag_id )
	restored_flag = ""
	for p in payload:
		restored_flag += chr( p[ 0 ] ) + chr( p[ 1 ] ) + chr( p[ 2 ] ) + chr( p[ 3 ] )
	if restored_flag != flag:
		close(CORRUPT, "Service corrupted", "Invalid flag: %s" % restored_flag )

	close( OK )


##
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
