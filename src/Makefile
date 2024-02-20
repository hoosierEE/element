# %.cc = runtime.cc main.cc
W = --Werror all-warnings

.PHONY: clean test

SOURCES = runtime.cc main.cc
OBJS = $(SOURCES:.cc=.o)

%.o: %.cc
	nvcc $(W) --compile $< --output-file $@

a.out: $(OBJS)
	nvcc $(W) $^

test: a.out
	bash -c './a.out <<<"2+3"'

clean:
	rm -f *.o a.out
