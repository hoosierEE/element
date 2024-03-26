# https://erikeidt.github.io/The-Double-E-Method
from typing import List
debug = print
def _debug(*a,**b): pass
RMAX = 0

bop = {# binary token:(precedence,arity,name) high precedence binds after low
 '*': (2,2,'mul'),
 '+': (2,2,'add'),
 '-': (2,2,'sub'),
 '(': (2,2,'fun'), # call
 ';': (3,2,'seq'), # separator
}

uop = {# unary
 '#': (2,1,'count'), # count
 '-': (2,1,'negate'), # negate
 '(': (2,1,'opa'), # open parenthesis for group/list
}

adv = {
 "'": (2,1,"each"), # each
 '/': (2,1,'reduce'), # reduce
 '\\':(2,1,'scan'), # scan
}

OW,DW = 20,31
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
 def next(s,inc=1): # peek() when inc=0
  if s.i<s.z:
   s.i += inc
   return s.s[s.i-inc]

 def unary(s):
  s.setstate('binary')
  if (op:=s.next()) is None:
   s.setstate('done')
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
   s.pushd(Ast('nil')) # insert "nil" left argument to ";"
   s.pusho(bop[op]) # then treat as if it was binary all along
   s.setstate('unary')
  elif op==')': # and s.peeko()[2] in ('fun','opa','seq'):
   if s.peeko()[2] in ('fun','opa','seq'):
    s.pushd(Ast('nil'))
    s.reduce_paren()
    # s.setstate('unary')
   else:
    s.pusho((1,2,'proj'))
    s.pushd(Ast('nil'))
    # s.pushd(Ast('lambda',Ast('x'),Ast(s.popo()[2],s.popd(),Ast('x'))))
    s.reduce_paren()
  elif op in uop:
   s.pusho(uop[op])
   s.setstate('unary')
  elif op in adv:
   debug(s,'op in adv')
   p,a,o1 = s.popo()
   _,_,o2 = adv[op]
   s.pusho((p,a,f'({o2} {o1})'))
   s.setstate('unary')
  else: # projections like f[;;z] or (2+) can be converted to lambdas
   print('  projection')
   s.pusho((0,1,'prj')) # projection
   s.reduce_paren()
   s.setstate('unary')

 def reduce_match(s,op):
  while True:
   if not s.o:
    return s.error('unexpected ")"')
   p,a,o = s.peeko()
   if o == op:
    break
   s.reduce_top(*s.popo())

 def reduce_prec(s,prec):
  while s.o and s.state != 'error':
   p,a,op = s.peeko()
   if op in ('fun','lst','opa') or prec>=p:
    break
   s.reduce_top(*s.popo())

 def reduce_top(s,p,a,op):
  if op in ('fun','lst','opa'):
   return s.error('unmatched (')
  args = [s.popd() for _ in range(a)][::-1]
  s.merge_seq(args,op)
  # s.pushd(Ast(op,*args))

 def merge_seq(s,args,name):
  if name=='seq' and args[1].node=='seq':
   a,b = args
   bs = (Ast(x) for x in b.children)
   s.pushd(Ast(name,a,*bs))
  elif name=='opa' and args[0].node=='seq':
   s.pushd(Ast('lst',*args[0].children))
  else:
   s.pushd(Ast(name,*args))

 # def reduce(s,prec:int,*matches:tuple):
 #  while s.o and s.state != 'error': # until operator stack empty
 #   p,arity,name = s.peeko()
 #   if name in matches:        return debug('  bail')
 #   if len(s.d)<arity:         return debug('  arity')
 #   if not matches and p>prec: return debug('  precedence')
 #   # if name in matches or len(s.d)<arity or p<=prec: return debug('  bail')
 #   s.popo()
 #   args = [s.popd() for _ in range(arity)][::-1]
 #   if name=='seq' and args[1].node=='seq': # merge repeated ";" into single "seq"
 #    a,b = args
 #    bs = (Ast(x) for x in b.children)
 #    s.pushd(Ast(name,a,*bs)) # (cons a (cons b c)) => (a b c)
 #   elif name=='opa' and args[0].node=='seq':
 #    s.pushd(Ast('lst',*args[0].children))
 #   else:
 #    s.pushd(Ast(name,*args))
 #   debug(s,'reduce')


 def reduce_paren(s):
  debug(s,'rp0')
  s.reduce(RMAX,'fun','opa')
  if not s.o: return
  debug(s,'rp1')
  t = s.popo()
  if not t or t[2] not in ('fun','opa'):
   return s.error('unmatched ")" (1)')
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
   while s.o and s.state != 'error':
    p,a,o = s.peeko()
    print(s,p,a,o)
    if o=='fun':
     s.popo()
     args = [s.popd() for _ in range(a)][::-1]
     s.merge_seq(args,o)
     return
    s.reduce_top(*s.popo())
   # s.reduce_match(bop['('][2])
   # s.reduce_paren()
  elif s.next(0) in adv:
   p,a,o1 = bop[op]
   _,_,o2 = adv[s.next()]
   s.pusho((p,a,f'({o2} {o1})'))
   s.setstate('unary')
  elif op in bop:
   debug(s,'binary()')
   s.reduce_prec(bop[op][0])
   s.pusho(bop[op])
   s.setstate('unary')
  else:
   s.error('unknown binary op')

 def parse(s):
  debug(f' {"operators":^{OW}}   {"data":^{DW}}    state     current token')
  while s.state in ('binary','unary'):
   debug(s)
   s.unary() if s.state=='unary' else s.binary()
  if s.state == 'error': return None
  debug(s,'final reduce')
  while s.o:
   s.reduce_top(*s.popo())
  if s.o:        return s.error(f'incomplete. {len(s.o)} items left on operator stack')
  if len(s.d)>1: return s.error(f'incomplete. {len(s.d)} items left on data stack')
  if s.state == 'done' and len(s.o) == 0: return s.popd()
  if s.o == [bop[';']]:
   if len(s.d)==1: return Ast('shy',s.popd())#  if len(s.d)<2 else 'seq',s.popd())
  if s.o and s.popo()[2]=='seq': return Ast('shy' if len(s.d)==1 else 'seq', *s.d)
  # return s.d[0] if len(s.o)==0 and len(s.d)==1 and s.state=='done' else None


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 # def __eq__(s,other):
 #  return s.node==other.node and s.children==other.children
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
 # assert repr(parse("(2-(3+))a")) == TODO

if __name__ == "__main__":
 test()
