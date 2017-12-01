import sys

data = sys.stdin.read()

output = [ 
	'#pragma once', 
	'#include "types.h"', 
	'', 
	'byte face[] = { %s };' % ', '.join([hex(ord(c)) for c in data]) ]


for l in output:
	print(l)