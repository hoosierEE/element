# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from Scanner import Scanner

debug = print
# def debug(*args,**kwargs): pass

bop = { #{token : (bp, arity, name)}
 '+': (5,2,'add'),
 '-': (5,2,'sub'), # subtract
 '*': (5,2,'mul'), # multiply
 '%': (5,2,'div'), # divide
 '^': (5,2,'pow'), # power
 '=': (5,2,'equ'), # equals
 ':': (5,2,'imm'), # immutable name binding
 '::':(5,2,'mut'), # mutable binding or update
 '[': (6,2,'arg'), # pops: name from s.o, arglist from s.d
 ';': (6,2,'sep'), # argument or list item separator
 # ']': (8,0,'gra'), # arglist
 # ')': (8,0,'cpa'),
 '':  (9,0,'fin'), # end of tokens
}

uop = {
 '-': (5,1,'neg'), # negate
 '*': (5,1,'fir'), # first
 '+': (5,1,'flp'), # flip
 '=': (5,1,'grp'), # group
 '%': (5,1,'sqr'), # square root
 # ';': (6,1,'skp'), # skip
 '(': (6,0,'opa'), # open paren for (grouping) (and;lists)
 '[': (6,1,'prg'), # progn
 ')': (8,0,'cpa'), # close paren
 ']': (0,0,'nil'), # emtpy argument list "nilad"
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
 def error(s,msg): debug('ERROR: '+msg);s.state = 'error'
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
  '''
  In unary state, a closing token like ")" or "]" implies projection as in
  "(3+)" and "f[x;]" (meanwhile "f[;x]" is another kind of projection) or a
  progn like "[x;]" with an empty final expression.

  Else, we have "(" or "[" to start a list or progn, or unary ops, or operands.
  '''
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
   s.pushd(Ast('array',*nums) if len(nums)>1 else Ast(*nums))
  elif op.isalnum(): s.pushd(Ast(op)) # name

  # handle ] or ) in unary state which must be one of:
  # - empty arglist: f[]
  # - function projection: f[a;]
  # - list/progn ending with nil: (a;) [a;]
  # - parenthesized projection: (2+)

  elif op == ']':
   # s.reduce_square(op)
   if s.peeko()[2] in ('prg','sep'): # [;]
    s.pushd(Ast('nil'))
    s.reduce_square(op)
   elif s.popo()[2] == 'arg': # f[]
    s.pushd(Ast(s.popo()[2],Ast(uop[op][2])))
   else:
    return s.error('unmatched "]"')

  elif op == ')':
   if s.peeko()[2] in ('opa','sep'):
    s.pushd(Ast('nil'))
    s.reduce_paren(op)
   elif s.popo()[2] == 'list':
    s.pushd(Ast(s.popo()[2],Ast(uop[op][2])))
   else:
    s.error('unmatched ")"')

  elif op == ';': # leading ";" as in (;x) or ";x" or "2+;x" - reduce up to ";"
   s.pushd(Ast('nil'))
   s.pusho(bop[op]) # NOTE: binary op even though we're in unary state, for (;m)
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
  if name == 'sep' and args[-1].node == 'sep': # merge
   a,b = args
   s.pushd(Ast(name,a,*b.children)) # (cons a (cons b c)) => (a b c)
   print(s,"merge sep")
  elif name == 'prg' and args[-1].node == 'sep': # (prg (sep ...)) => (prg ...)
   s.pushd(Ast(name,*args[-1].children))
   print(s,'merge prg')
  else:
   s.pushd(Ast(name,*args))

 def reduce(s,src:dict,op:str):
  while s.o and s.state != 'error':
   p,arity,name = s.peeko()
   if p>=src[op][0]: break
   # if name in ('arg','opa') or p>=src[op][0]: break
   s.reduce_top(src,op)

 def reduce_paren(s,op):
  while s.o:
   s.reduce(bop,op)
   p,arity,nm = s.peeko()
   if nm == 'opa':
    s.popo()
    if s.peekd().node == 'sep': # merge
     s.pushd(Ast('list',*s.popd().children)) # (a;b;c;d;e)
    break
   args = [s.popd() for _ in range(arity)][::-1]
   s.pushd(Ast(nm,*args)) # reduce top operator

 def reduce_square(s,op):
  while True:
   s.reduce(bop,op)
   if not s.o: return
   p,arity,nm = s.peeko()
   if nm == 'arg':
    s.popo()
    break # reduce until 'arg', then build funcall node
   if nm == 'prg':
    break
   args = [s.popd() for _ in range(arity)][::-1]
   s.pushd(Ast(nm,*args)) # reduce top operator
  # if s.peekd() is None:
  #  s.pushd(Ast(nm,s.popo()))
  if s.peekd().node == 'sep': # merge
   print("merging")
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

  elif op == ')':
   s.reduce_paren(op)

  elif op == ']':
   s.reduce_square(op)
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
   if s.state == 'unary': debug(s); s.unary()
   elif s.state == 'binary': debug(s); s.binary()
   else: break
  if s.state == 'done': s.reduce(bop,'')
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

def parse(s): return Parser(Scanner(s).tokens).parse()

if __name__ == "__main__":
 test()

