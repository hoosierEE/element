# grammar:
# s ::= e (";" e)*
# e ::= (n v | t)*
# t ::= n | v
# v ::= t "A" | "V"
# n ::= "N" | t "[" s "]" | "(" s ")" | "{" s "}"
# rules = {
#  "s": ("s;e","e"),
#  "e": ("nve","ne","ve"),
#  "v": ("nA","vA","V"),
#  "n": ("N","n[s]","v[s]","(s)","{s}"),
# }
# rrule = {vi:k for k,v in rules.items() for vi in v}

class Lexer:
 def __init__(self,s):
  self.EOF = "EOF"
  self.s = list(s) + [self.EOF]

 def next(self):
  h,*self.s = self.s
  return h

 def peek(self):
  return s[0]

def ex(s):
 l = Lexer(s)
 lhs = l.next()
 while True:
  match l.peek():
   case "EOF": break
   case op:
   case _: return False

 return lhs


def tests():
 assert ex("1") == "1"
 # assert ex("1+2*3") == "(+ 1 (* 2 3))"

tests()
