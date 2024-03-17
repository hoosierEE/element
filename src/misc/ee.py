# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from Scanner import Scanner

debug = print
# def debug(*args,**kwargs): pass

bop = { #{token : (bp, arity, name)}
 '+': (5,2,'add'),
 '-': (5,2,'sub'),
 '*': (5,2,'mul'),
 '%': (5,2,'div'),
 '^': (5,2,'pow'),
 '=': (5,2,'equ'),
 ':': (5,2,'imm'), # immutable name binding
 '::':(5,2,'mut'), # mutable binding or update
 ';': (6,2,'sep'), # argument or list item separator
 '[': (5,2,'arg'), # pops: name from s.o, arglist from s.d
 ']': (8,0,'arg'), # arglist
 ')': (8,0,'cpa'),
 '':  (9,0,'fin'), # end of tokens
}

uop = {
 '-': (5,1,'neg'),
 '*': (5,1,'1st'),
 '+': (5,1,'flp'),
 '=': (5,1,'grp'),
 '%': (5,1,'sqr'),
 # ';': (6,1,'skp'), # skip
 # ')': (8,0,'cpa'),
 '(': (4,0,'opa'), # open paren for grouping (-a)+b (and;for;lists)
 '[': (5,0,'prg'), # progn
 ']': (8,0,'nil'), # emtpy argument list "nilad"
}

class Parser:
 def __init__(s,tokens):
  s.state = 'unary' # current state : Literal['unary','binary','error','done']
  s.o = []          # operator stack : List[Tuple[bp:int,arity:int,description:str]]
  s.d = []          # AST node stack : List(Ast) (should end with 0 or 1)
  s.s = tokens      # raw string : str
  s.i = 0           # index of current token : int
  s.z = len(tokens) # last index + 1 : int
 def __repr__(s):   # return ' '.join(s.s[:s.i])+'¦'+' '.join(s.s[s.i:])
  o = ' '.join(x[2] for x in s.o)
  d = ' '.join(map(repr,s.d))
  t = f'{s.state}'
  return f'[{o:<30}]  [{d:<50}]  {t:<8}  "{s.s[s.i] if s.i<s.z else ""}"'
 def peekd(s): return s.d[-1] if s.d else None
 def peeko(s): return s.o[-1] if s.o else None
 def popd(s): return s.d.pop()
 def popo(s): return s.o.pop()
 def pushd(s,x): s.d.append(x)
 def pusho(s,x): s.o.append(x)
 def error(s,msg):
  debug(msg)
  s.state = 'error'
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
    else: s.i -= 1; break
   s.pushd(Ast('array',*nums) if len(nums)>1 else Ast(*nums))
  elif op.isalnum(): s.pushd(Ast(op)) # name
  elif op == ']':
   if s.popo()[2] != 'arg': return s.error('unmatched bracket')
   s.pushd(Ast(s.popo()[2],Ast('args')))
  elif op == ';':
   s.pushd(Ast('nil'))
   s.pusho(bop[op]) # NOTE: binary op even though we're in unary state, for f[n;] and (;m;)
   s.setstate('unary')
  elif op in uop:
   s.pusho(uop[op])
   s.setstate('unary')
  else: s.error(f'unidentified unary op: {op}')


 def reduce_top(s,src:dict,op:str):
  p,arity,name = s.popo()
  if len(s.d) < arity:
   return s.error("not enough arguments on data stack")
  args = [s.popd() for _ in range(arity)][::-1]
  if name=='sep' and args[1].node == 'sep':
   a,b = args
   s.pushd(Ast(name,a,*b.children))
  else:
   s.pushd(Ast(name,*args))
  print(s)

 def reduce(s,src:dict,op:str):
  while s.o:
   p,arity,name = s.peeko()
   if name in ('arg','opa') or p>=src[op][0]: break
   s.reduce_top(src,op)

 def binary(s):
  op = s.next()
  while op and op.isspace():
   op = s.next() # consume whitespace tokens
  if op is None:
   return s.setstate('done')

  elif op == '[': # in binary state, '[' means 'call'
   fn = s.popd().node # extract function name
   s.pusho((5,-1,fn)) # push name to op stack (defer arity to runtime)
   s.pusho(bop[op]) # show ] where to stop
   s.setstate('unary')

  elif op == ')':
   while s.o:
    s.reduce(bop,op)
    p,arity,nm = s.peeko()
    if nm == 'opa':
     s.popo()
     if s.peekd().node == 'sep': # (a;b;c;d;e)
      s.pushd(Ast('list',*s.popd().children))
     break
    args = [s.popd() for _ in range(arity)][::-1]
    s.pushd(Ast(nm,*args)) # reduce top operator

  elif op == ']':
   while s.o:
    s.reduce(bop,op)
    p,arity,nm = s.peeko()
    if nm == 'arg':
     s.popo()
     if s.peekd().node == 'sep': # [x;y;z]
      s.pushd(Ast('args',*s.popd().children))
     else:
      s.pushd(Ast('args',s.popd()))
     break # reduce until 'arg', then build funcall node
    args = [s.popd() for _ in range(arity)][::-1]
    s.pushd(Ast(nm,*args)) # reduce top operator
   s.pushd(Ast(s.popo()[2],s.popd())) # now push the function call itself
   s.setstate('binary')

  elif op in bop:
   s.reduce(bop,op)
   s.pusho(bop[op])
   s.setstate('unary')

  else:
   s.setstate('error')

 def parse(s):
  debug(f' {"operators":^30}   {"data":^50}    state     next token')
  while True:
   if s.state == 'unary': debug(s);s.unary()
   elif s.state == 'binary': debug(s);s.binary()
   else: break
  if s.state == 'done':
   print('done')
   s.reduce(bop,'')
  else:
   toks = ' '.join(s.s[:s.i])
   debug("'parse\n"+toks+'\n'+(len(toks)-1)*" "+"^")
  assert len(s.d)<2, "leave at most one AST node on the stack"
  return s.d[0] if len(s.d) else []


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  if not s.children: return f'{s.node}'
  # return f'({s.node} {" ".join(map(repr,s.children))})' # lisp style
  return f'{s.node}({",".join(map(repr,s.children))})' # c-style
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

if __name__ == "__main__":
 test()

