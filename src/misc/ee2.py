# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from typing import List
debug = print
def _debug(*a,**b): pass
# token:(order,arity,name) high order binds after low order
bop = {
 '(': (1,1,'fun'), # function call
 '#': (2,2,'cpy'), # copy
 '%': (2,2,'div'), # divide
 '&': (2,2,'min'), # min/and
 '*': (2,2,'mul'), # multiply
 '+': (2,2,'add'), # add
 ',': (2,2,'joi'), # join
 '-': (2,2,'sub'), # subtract
 '<': (2,2,'les'), # less
 '=': (2,2,'equ'), # equal
 '>': (2,2,'mor'), # more
 '|': (2,2,'max'), # max/or
 '~': (2,2,'mat'), # match
 ';': (4,2,'seq'), # expression or argument separator
 ')': (9,0,'cpa'), # close paren
 '':  (9,0,'fin'), # no more tokens
}

uop = {
 '#': (2,1,'cnt'), # count
 '%': (2,1,'sqr'), # square root
 '&': (2,1,'whe'), # where
 '*': (2,1,'fst'), # first
 '+': (2,1,'flp'), # flip
 ',': (2,1,'rav'), # ravel
 '-': (2,1,'neg'), # negate
 '<': (2,1,'gru'), # grade up
 '=': (2,1,'grp'), # group
 '>': (2,1,'grd'), # grade down
 '|': (2,1,'rev'), # reverse
 '~': (2,1,'not'), # logical not
 ')': (3,0,'arg'), # empty arglist
 '(': (9,1,'opa'), # open paren - could be for grouping or starting a list
}

adv = {
 "'": (2,1,"ech"), # each
 '/': (2,1,'red'), # reduce
 '\\':(2,1,'scn'), # scan
}

OW,DW = 20,20
class Parser:
 def __init__(s,tokens:List[str]):
  s.state = 'unary' # current state : Literal['unary','binary','error','done']
  s.o = []          # operator stack : List[Tuple[bp:int,arity:int,description:str]]
  s.d = []          # AST node stack : List(Ast) (should end with 0 or 1)
  s.s = tokens      # raw string : str
  s.i = 0           # index of current token : int
  s.z = len(tokens) # last index + 1 : int
  s.m = ''
 def __repr__(s):
  o = ' '.join(x[2] for x in s.o)
  d = ' '.join(map(repr,s.d))
  t = f'{s.state}'
  return f'[{o:<{OW}}]  [{d:<{DW}}]  {t:<8}  "{s.s[s.i] if s.i<s.z else ""}"'
 def peeko(s): return s.o[-1] if s.o else None
 def popd(s): return s.d.pop()
 def popo(s): return s.o.pop()
 def pushd(s,x): s.d.append(x)
 def pusho(s,x): s.o.append(x)
 def error(s,msg):
  s.state = 'error'
  s.m = msg
  toks = ' '.join(s.s[:s.i])
  print("'PARSE:",s.m)
  print(toks,' '.join(s.s[s.i:]))
  print((len(toks)-1)*" "+"^")
 def setstate(s,newstate):
  if newstate not in ('binary','unary','done'): raise
  if s.state in ('done','error'): return # don't change either of these states
  s.state = newstate
 def end(s): return s.i>=s.z
 def next(s,inc=1): # doubles as peek() when inc=0
  if s.end(): return None
  x = s.s[s.i]
  s.i += inc
  return x


 def unary(s):
  s.setstate('binary')
  if (op:=s.next()) is None:
   s.setstate('done')
  elif s.next(0) in adv: # must handle this before "-"
   p,a,o1 = uop[op]
   _,_,o2 = adv[s.next()]
   s.pusho((p,a,o2+"."+o1)) # derived verb
   s.setstate('unary')
  elif op.isnumeric() or op=='-':
   if op=='-':
    if not s.next(0).isnumeric():
     s.pusho(uop[op]) # unary minus
     s.setstate('unary')
     return
    s.pushd(Ast(op+s.next())) # negative number
   else:
    s.pushd(Ast(op))
  elif op.isalnum():
   s.pushd(Ast(op)) # name
  elif op==';':
   s.pushd(Ast('()')) # add "()" left argument to ","
   s.pusho(bop[op]) # treat as binary
   s.setstate('unary')
  elif op==')':
   if s.peeko()[2] in ('fun','seq'):
    s.pushd(Ast('()'))
    s.reduce_paren()
   else:
    s.pushd(Ast('()'))
    s.popo()
  elif op in uop:
   s.pusho(uop[op])
   s.setstate('unary')
  elif op in adv:
   s.pusho(adv[op])
   s.setstate('unary')
  else:
   s.error(f'unidentified unary op: {op}')


 def reduce(s,prec:int,*matches:tuple):
  while s.o and s.state != 'error':
   p,arity,name = s.peeko()
   if len(s.d)<arity: return
   if matches and name in matches: return
   if name=='fun': return
   if p>=prec: return
   s.popo()
   args = [s.popd() for _ in range(arity)][::-1]
   if name=='seq' and args[1].node=='seq':
    a,b = args
    bs = (Ast(x) for x in b.children)
    s.pushd(Ast(name,a,*bs)) # (cons a (cons b c)) => (a b c)
   else:
    s.pushd(Ast(name,*args))


 def reduce_paren(s):
  s.reduce(9)
  if not s.o: return s.error('unmatched ")"')
  t = s.popo()
  if not t or t[2] not in ('fun','opa'):
   return s.error('unmatched ")"')
  args = s.popd()
  fn = s.popd() if t[2]=='fun' else t[2]
  ch = args.children if args.node=='seq' else (args,) # tuple-ify for next step: *ch
  if fn=='opa':
   s.pushd(Ast('lst',*ch) if args.node=='seq' else Ast(*ch))
  else:
   s.pushd(Ast(fn,*ch))

 def binary(s):
  if (op:=s.next()) is None:
   s.setstate('done')
  elif op == ')': # (a;b) and function calls: f(x;y)
   s.reduce_paren()
  elif s.next(0) in adv:
   p,a,o1 = bop[op]
   _,_,o2 = adv[s.next()]
   s.pusho((p,a,o2+"."+o1))
   s.setstate('unary')
  elif op in bop:
   s.reduce(bop[op][0])
   s.pusho(bop[op])
   s.setstate('unary')
  else:
   s.error('unknown binary op')


 def parse(s):
  debug(f' {"operators":^{OW}}   {"data":^{DW}}    state     next token')
  while s.state in ('binary','unary'):
   debug(s)
   s.unary() if s.state=='unary' else s.binary()
  s.reduce(bop[''][0]) # reduce harder
  if s.state == 'error':
   return None
  if s.o == [bop[';']]:
   return Ast('shy',s.popd())#  if len(s.d)<2 else 'seq',s.popd())
  if len(s.d)==1:
   return s.popd()
  debug(s,'after last reduce')
  if s.o and s.popo()[2]=='seq':
   return Ast('shy',*s.d) if len(s.d)==1 else Ast('seq',*s.d)
  return s.d[0] if len(s.o)==0 and len(s.d)==1 and s.state=='done' else None


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __eq__(s,other):
  return s.node==other.node and s.children==other.children
 def __repr__(s):
  if not s.children and s.node != 'list': return f'{s.node}'
  return f'({s.node} {" ".join(map(repr,s.children))})' # lisp style

def parse(s:str):
 '''trivial tokenizer: single char tokens, no spaces'''
 return Parser(list(s)).parse()

def test(verbose=0):
 global debug
 debug = print if verbose else _debug
 assert repr(parse("-a+b-c")) == "(neg (add a (sub b c)))"
 assert repr(parse("-(a+b)-c")) == "(neg (sub (add a b) c))"
 assert repr(parse("(-a)+b-c")) == "(add (neg a) (sub b c))"
 assert repr(parse("a+b;0;c-d")) == "(seq (add a b) 0 (sub c d))"
 assert repr(parse("f()")) ==  "(f ())"
 assert repr(parse("f(x)")) ==  "(f x)"
 assert repr(parse("f(x;)")) ==  "(f x ())"
 assert repr(parse("f(;x)")) ==  "(f () x)"
 assert repr(parse("f(x;y)")) ==  "(f x y)"
 assert repr(parse("f(-a;b)")) ==  "(f (neg a) b)"
 assert repr(parse("x+f()")) ==  "(add x (f ()))"
 assert repr(parse("x;f()")) == "(seq x (f ()))"
 assert repr(parse("-a;c")) == "(seq (neg a) c)"

if __name__ == "__main__":
 test()
