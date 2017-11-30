.PHONY: debug release clean

debug:
	g++ -O0 -g -std=c++11 main.cpp png.cpp gpu.cpp httpserver.cpp ship.cpp -DDEBUG=1 -lmicrohttpd -l3ds -luuid -o raster-dbg
	
release:
	g++ -O2 -g -std=c++11 compiler.cpp -fstack-protector-all -o compiler
	g++ -O2 -g -std=c++11 disasm.cpp -fstack-protector-all -o disasm
	g++ -O2 -g -std=c++11 main.cpp png.cpp gpu.cpp httpserver.cpp ship.cpp -fstack-protector-all -lmicrohttpd -l3ds -luuid -o raster

start:
	/home/raster/raster

serve: release start
