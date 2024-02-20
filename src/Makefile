SHELL := /bin/bash
# type `make` like normal to target GPU:
# $ make test
CC = nvcc
W = --Werror all-warnings
CFLAGS = --compile
OFLAGS = --output-file
# ...or set `CPU=1` to target CPU instead:
# $ CPU=1 make test
ifdef CPU
CC = g++
W = -Werror -Wall
CFLAGS = -c
OFLAGS = -o
endif

SOURCES = lexer.cc parser.cc main.cc
OBJS = $(SOURCES:.cc=.o)
%.o: %.cc;      $(CC) $(W) $(CFLAGS) $< $(OFLAGS) $@
a.out: $(OBJS); $(CC) $(W) $^
.PHONY: clean test
clean:; rm -f *.o a.out
T0 = "TEST(lex):"
T1 = "TEST(parse):"
test: a.out
	@ R=$$(./a.out<<<"2.1" 2>&1);if [[ $$R == *"ERROR"* ]];then echo $(T0)$$R;fi
	@ R=$$(./a.out<<<"2.b" 2>&1);if [[ $$R != *"ERROR"* ]];then echo $(T0)$$R;fi
	@ R=$$(./a.out<<<"2a"  2>&1);if [[ $$R != *"ERROR"* ]];then echo $(T0)$$R;fi
