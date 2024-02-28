SHELL := /bin/bash
ifdef CPU
CC = g++
W = -Werror -Wall
# retain color when piping output to less/more:
# CPU=1 make clean test 2>&1 | less -R
CFLAGS = -c -fdiagnostics-color -g
OFLAGS = -o
else
CC = nvcc
W = --Werror all-warnings
CFLAGS = --compile
OFLAGS = --output-file
endif

SOURCES = lexer.cc parser.cc main.cc
OBJS = $(SOURCES:.cc=.o)
# OBJS += $(SOURCES:.cu=.o)
%.o: %.cc;      $(CC) $(W) $(CFLAGS) $< $(OFLAGS) $@
a.out: $(OBJS); $(CC) $(W) $^
.PHONY: clean test
clean:; rm -f *.o a.out
T0 = "TEST(lex):"
T1 = "TEST(parse):"
test: a.out
	@ R=$$(./a.out<<<"2.1" 2>&1);if [[ $$R == *"ERROR"* ]];then echo $(T0)$$R;fi
	@ R=$$(./a.out<<<"2.b" 2>&1);if [[ $$R != *"SYNTAX ERROR"* ]];then echo $(T0)$$R;fi
	@ R=$$(./a.out<<<"2a"  2>&1);if [[ $$R != *"SYNTAX ERROR"* ]];then echo $(T0)$$R;fi
