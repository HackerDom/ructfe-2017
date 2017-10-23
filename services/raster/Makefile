.PHONY: debug all compiler disasm release clean

debug:
	g++ -O0 -g -std=c++11 main.cpp png.cpp -DDEBUG=1 -lpng12 -o raster-dbg

compiler:
	g++ -O0 -g -std=c++11 compiler.cpp -o compiler

disasm:
	g++ -O0 -g -std=c++11 disasm.cpp -o disasm
	
all: debug compiler disasm

release:
	g++ -O2 -std=c++11 main.cpp png.cpp -lpng12 -o raster
