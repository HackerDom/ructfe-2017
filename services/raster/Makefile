.PHONY: debug all compiler disasm release clean

debug:
	g++ -O0 -g -std=c++11 main.cpp png.cpp gpu.cpp httpserver.cpp ship.cpp -DDEBUG=1 -lmicrohttpd -l3ds -luuid -o raster-dbg

compiler:
	g++ -O0 -g -std=c++11 compiler.cpp -o compiler

disasm:
	g++ -O0 -g -std=c++11 disasm.cpp -o disasm
	
all: debug compiler disasm

release:
	g++ -O2 -std=c++11 main.cpp png.cpp gpu.cpp httpserver.cpp ship.cpp -lmicrohttpd -l3ds -luuid -o raster

start:
	/home/raster/raster

serve: release start
