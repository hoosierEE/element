# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from Scanner import Scanner
debug = print
# def debug(*args,**kwargs): pass

bop = { # token:(order,arity,name) high order binds later than low order
 '+': (5,2,'add'),
 '-': (5,2,'sub'),
 '*': (5,2,'mul'),
 '[': (6,2,'osq'), # function call
 ';': (6,2,'sep'), # argument or list item separator
 ']': (8,0,'csq'), # arglist
 ')': (8,0,'cpa'), # close paren
 '':  (9,0,'fin'), # end of tokens
}

uop = {
 '+': (5,1,'flp'), # flip
 '-': (5,1,'neg'), # negate
 '(': (6,1,'opa'), # open paren for (grouping-items) (or;for;lists)
 '[': (6,1,'prg'), # progn
 ')': (8,0,'cpa'), # close paren
 ']': (8,0,'csq'), # f[] (nilad)
 '':  (9,0,'fin'), # end of tokens
}

OW,DW = 20,30
class Parser:
 def __init__(s,tokens):
  s.state = 'unary' # current state : Literal['unary','binary','error','done']
  s.o = []          # operator stack : List[Tuple[bp:int,arity:int,description:str]]
  s.d = []          # AST node stack : List(Ast) (should end with 0 or 1)
  s.s = tokens      # raw string : str
  s.i = 0           # index of current token : int
  s.z = len(tokens) # last index + 1 : int
  s.m = ''
 def __repr__(s):   # return ' '.join(s.s[:s.i])+'¦'+' '.join(s.s[s.i:])
  o = ' '.join(x[2] for x in s.o)
  d = ' '.join(map(repr,s.d))
  t = f'{s.state}'
  return f'[{o:<{OW}}]  [{d:<{DW}}]  {t:<8}  "{s.s[s.i] if s.i<s.z else ""}"'
 def peekd(s): return s.d[-1] if s.d else None
 def peeko(s): return s.o[-1] if s.o else None
 def popd(s): return s.d.pop()
 def popo(s): return s.o.pop()
 def pushd(s,x): s.d.append(x)
 def pusho(s,x): s.o.append(x)
 def error(s,msg):
  s.state = 'error'
  s.m = msg
  print("'PARSE:",s.m)
  print(' '.join(s.s[:s.i]),' '.join(s.s[s.i:]))
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
  op = s.next()
  s.setstate('binary')
  while op and op.isspace(): op = s.next() # consume leading whitespace
  if op is None: return s.setstate('done')
  elif op.isnumeric() or op=='-':
   if op=='-':
    if not s.next(0).isnumeric():
     s.pusho(uop[op])
     s.setstate('unary')
     return
    nums = [Ast(op+s.next())]
   else: nums = [Ast(op)]
   space = 0 # stranding
   while (op := s.next()):
    if op.isspace():
     space = 1
     continue
    elif op.isnumeric(): nums.append(Ast(op))
    elif space and op=='-' and s.next(0).isnumeric():
     nums.append(Ast('-'+s.next()))
     space = 0
    else: s.i -= 1;break
   s.pushd(Ast('array',*nums) if len(nums)>1 else Ast(*nums)) # array or int
  elif op.isalnum(): s.pushd(Ast(op)) # name
  elif op == ']': s.pushd(Ast('nil'));s.reduce_square(uop,op)
  elif op == ')':
   if s.peeko()[2] == 'opa': s.pushd(Ast('list',Ast('nil')))
   else:s.pushd(Ast('nil'))
   s.reduce_paren(uop,op)
  elif op == ';': s.pushd(Ast('nil'));s.pusho(bop[op]);s.setstate('unary')
  elif op in uop: s.pusho(uop[op]);s.setstate('unary')
  else: s.error(f'unidentified unary op: {op}')


 def reduce(s,src:dict,op:str):
  while s.o and s.state != 'error':
   p,arity,name = s.peeko()
   if p>=src[op][0] or name in ('osq','opa'): break # stop if you reach "[" or "("
   s.reduce_top(src,op)

 def reduce_top(s,src:dict,op:str):
  p,arity,name = s.popo()
  if len(s.d) < arity: s.error("not enough arguments on data stack"); return
  args = [s.popd() for _ in range(arity)][::-1]
  if name == 'sep' and args[-1].node == 'sep': # merge
   a,b = args
   s.pushd(Ast(name,a,*b.children)) # (cons a (cons b c)) => (a b c)
  elif name == 'prg' and args[-1].node == 'sep': # (prg (sep ...)) => (prg ...)
   s.pushd(Ast(name,*args[-1].children))
  else: s.pushd(Ast(name,*args))

 def reduce_paren(s,src,op):
  while True:
   s.reduce(src,op)
   if not s.o: return
   p,arity,nm = s.peeko()
   if nm == 'opa': # reduce until no more stack or found "("
    s.popo()
    if s.peekd().node == 'sep': # merge ";"
     k = s.popd().children
     # if any(x.node == 'nil' for x in k): return s.error("empty expression in list")
     s.pushd(Ast('list',*k))
    break
   args = [s.popd() for _ in range(arity)][::-1]
   s.pushd(Ast(nm,*args)) # reduce top operator

 def reduce_square(s,src,op):
  while True:
   s.reduce(src,op)
   if not s.o: return
   p,arity,nm = s.peeko()
   if nm == 'osq':
    s.popo()
    break # reduce until 'osq', then build funcall node
   if nm == 'prg':
    break
   args = [s.popd() for _ in range(arity)][::-1]
   s.pushd(Ast(nm,*args)) # reduce top operator
  if s.peekd() is None:
   s.pushd(Ast(nm,s.popo()))
  elif s.peekd().node == 'sep': # merge
   s.pushd(Ast(s.popo()[2],*s.popd().children)) # [x;y;z]
  else:
   s.pushd(Ast(s.popo()[2],s.popd()))

 def binary(s):
  op = s.next()
  while op and op.isspace(): op = s.next() # consume whitespace tokens
  if op is None: return s.setstate('done')
  elif op == '[': # in binary state, '[' means 'call'
   fn = s.popd().node # extract function name
   s.pusho((5,-1,fn)) # push name to op stack (defer arity to runtime)
   s.pusho(bop[op]) # show ] where to stop
   s.setstate('unary')
  elif op == ')': s.reduce_paren(bop,op)
  elif op == ']': s.reduce_square(bop,op)
  elif op in bop:
   s.reduce(bop,op)
   s.pusho(bop[op])
   s.setstate('unary')
  else: s.error('unknown binary op')

 def parse(s):
  debug(f' {"operators":^{OW}}   {"data":^{DW}}    state     next token')
  while s.state in ('binary','unary'):
   s.unary() if s.state=='unary' else s.binary()
   debug(s)
  if s.state == 'error': return None
  s.reduce(bop,'')
  debug(s)
  if s.o and s.peeko()[2] in ('opa','osq','prg'): return s.error("unmatched bracket/paren")
  return s.d[0] if len(s.o)==0 and len(s.d)==1 and s.state=='done' else None


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 # def __eq__(s,other):
 #  return s.node == other.node and s.children == other.children
 def __repr__(s):
  if not s.children and s.node != 'list': return f'{s.node}'
  return f'({s.node} {" ".join(map(repr,s.children))})' # lisp style
  # return f'{s.node}({",".join(map(repr,s.children))})' # c-style
  # return f'{" ".join([repr(x) for x in s.children[::-1]])} {s.node}' # forth style (reverse args)


def test():
 a,b = Ast('1'),Ast('2')
 c = Ast('+', a, b)
 d,e = Ast('3'),Ast('4')
 f = Ast('*', c, d)
 g = Ast('-',f)
 assert f'{c}' == '(+ 1 2)'
 assert f'{f}' == '(* (+ 1 2) 3)'
 assert f'{g}' == '(- (* (+ 1 2) 3))'
 s = Scanner('3+42-abc99*34')
 assert ' '.join(s.tokens) == '3 + 42 - abc99 * 34'
 try:
  Scanner('2a')
  debug('ERROR: should have raised')
 except NameError:
  pass

 assert all(Parser(Scanner(x).tokens).parse() for x in ['2', '-2', 'a', 'a-a', '-a*b+c', '-a<3'])
 assert any(not Parser(Scanner(x).tokens).parse() for x in ['-', '-+', '+', 'a-'])
 debug('all good')

def parse(s): return Parser(Scanner(s).tokens).parse()

if __name__ == "__main__":
 test()

