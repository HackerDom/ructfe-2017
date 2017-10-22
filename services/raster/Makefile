.PHONY: debug all compiler disasm clean

debug:
	g++ -O0 -g main.cpp png.cpp -DDEBUG=1 -lpng16 -o raster-dbg

all:
	g++ -O2 main.cpp png.cpp -lpng16 -o raster

compiler:
	g++ -O0 -g compiler.cpp -o compiler

disasm:
	g++ -O0 -g disasm.cpp -o disasm
