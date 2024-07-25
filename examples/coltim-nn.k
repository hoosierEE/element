mmu:(+/*)\:                        / matrix-mul
sig:{1%1+`exp@-x}                  / sigmoid
infer:{sig mmu[x;y]}               / feed foward/run model

train:{[in;out;w]
  l:infer\[in;w]                   / feed forward
  f:(out-),{mmu[;+x]}'|1_w         / error calculations
  ld:{z*y x}\[*|l;f;|l*1-l]        / calculate deltas
  w+{mmu[+x;y]}'[(,in),-1_l;|ld]}  / update weights

in:-8?+2\!16                       / input data
out:8?2                            / output data

init:{x#1-(*/x)?2f}                / initialize weights
iw:init'(4 10;10 4;4 4;4 5;5)      / initialize layers

w:10000 train[in;out;]/iw          / train model

in!out,'infer/[in;w]               / model output

in2:+2\!16                         / full set of possible input
round:{(_0.5+x*1000)%1000}         / round output for display purposes
+(+2\!16)#0.0+0n^(in!out),'in2!round infer/[in2;w]
