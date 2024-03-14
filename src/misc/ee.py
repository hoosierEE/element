# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from Scanner import Scanner

debug = print
# def debug(*args,**kwargs): pass

bop = { #{token : (bp, arity, name)}
 '+': (10,2,'add'),
 '-': (10,2,'sub'),
 '*': (10,2,'mul'),
 '%': (10,2,'div'),
 '^': (10,2,'pow'),
 '=': (10,2,'equal'),
 ';': (90,2,'semi'),
 '[': (98,2,'fun'), # funcall (arity=2): (f: function name, [..]: argument list)
 ')': (99,0,'cparen'),
 '': (100,0,'finalizer'),
}

uop = {
 '-': (10,1,'negate'),
 '*': (10,1,'first'),
 '+': (10,1,'flip'),
 '=': (10,1,'group'),
 '%': (10,1,'sqrt'),
 '(': (99,0,'list'), # start group
 ']': (99,0,'empty_arglist'), # emtpy argument list
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
  return f'[{o:>30}]  [{d:<30}]  {t:<8}  {s.s[s.i] if s.i<s.z else " ":<5}'
 def peeko(s): return s.o[-1] if s.o else None
 def popd(s): return s.d.pop()
 def popo(s): return s.o.pop()
 def pushd(s,x): s.d.append(x)
 def pusho(s,x): s.o.append(x)
 def setstate(s,newstate,msg=''):
  if msg: debug(msg)
  if s.state in ('done','error'): return # don't change either of these states
  s.state = newstate
 def end(s): return s.i>=s.z
 def next(s,inc=1)->str|None: # doubles as peek() when inc=0
  if s.end(): return None
  x = s.s[s.i]
  s.i += inc
  return x


 def reduce_until(s,*matches):
  print('until')
  p,arity,name = s.peeko()
  while s.peeko() not in matches:
   debug(s,f'until{matches}')
   if not s.o:
    return s.setstate('error','unexpected emtpy stack')
   p,arity,name = s.popo()
   if name == 'fun':
    p,arity,name = s.popo() # discard 'fun' and use actual function (pushed earlier)
  args = [s.popd() for _ in range(arity)][::-1]
  s.pushd(Ast(name,*args))


 def reduce(s,src:dict,op:str):
  while s.o:
   p,arity,name = s.peeko()
   # if name in ('fun','list'): return
   if p >= src[op][0]: return # done for now
   if len(s.d) < arity: return s.setstate('error',"not enough arguments on data stack")
   _ = s.popo() # discard
   args = [s.popd() for _ in range(arity)][::-1]
   s.pushd(Ast(name,*args))


 def unary(s):
  op = s.next()
  s.setstate('binary')
  while op and op.isspace(): op = s.next() # consume whitespace tokens
  if op is None: return s.setstate('done')
  if op.isnumeric() or op=='-':
   if op=='-':
    if not s.next(0).isnumeric():
     s.setstate('unary')
     s.pusho(uop['-'])
     return
    nums = [Ast(op+s.next())]
   else:
    nums = [Ast(op)]
   while (op := s.next()):
    if op.isspace(): continue
    elif op.isnumeric(): nums.append(Ast(op))
    elif op=='-' and s.next(0).isnumeric(): nums.append(Ast('-'+s.next()))
    else: s.i -= 1; break
   print(nums)
   s.pushd(Ast('array',*nums) if len(nums)>1 else Ast(*nums))
  elif op.isalnum(): s.pushd(Ast(op)) # name
  elif op in uop:
   s.setstate('unary')
   if op == ']' and s.peeko() == bop['[']: return
   s.pusho(uop[op])
  else: s.setstate('error')


 def binary(s):
  op = s.next()
  while op and op.isspace(): op = s.next() # consume whitespace tokens
  if op is None: return s.setstate('done')

  # FIXME: TESTING
  if op in bop:
   s.reduce(bop,op)
   s.pusho(bop[op])
   s.setstate('unary')
  return

  if op == '[': # in binary state, '[' means function call
   s.reduce(bop,op)
   fn = s.popd().node # name, assume it's a function
   s.pusho((10,None,fn)) # push name to op stack (don't know arity)
   s.pusho(bop[op]) # show reduce_until where to stop
   s.setstate('unary')

  elif op == ']':
   s.reduce_until(bop['[']) # consumes '[', pushes args to s.d
   s.setstate('binary')

  # elif op == ')':
  #  s.reduce_until(uop['('])
  #  args = s.d.pop()
  #  tmp = []
  #  while args.node == 'semi':
  #   first,args = args.children
  #   tmp.append(first)
  #  if tmp:
  #   s.pushd(Ast(s.o.pop()[2],*(tmp+[args])))
  #  else:
  #   s.pushd(Ast(s.o.pop()[2],args))
  #  s.setstate('binary')

  elif op in bop:
   s.reduce(bop,op)
   s.pushd(bop[op])
   s.setstate('unary')

  else:
   s.setstate('error')

 def parse(s):
  debug(f' {"operators":^30}   {"data":^30}    state     next token')
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
  return f'({s.node} {" ".join(map(repr,s.children))})'
  # return f'{" ".join(map(repr,s.children))} {s.node}'


def test():
 a,b = Ast('1'),Ast('2')
 c = Ast('+', a, b)
 d,e = Ast('3'),Ast('4')
 f = Ast('*', c, d)
 g = Ast('-',f)
 s = Scanner('3+42-abc99*34')
 assert f'{c}' == '(+ 1 2)'
 assert f'{f}' == '(* (+ 1 2) 3)'
 assert f'{g}' == '(- (* (+ 1 2) 3))'
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

# bp    arity  operator
# 36    0      PrecedenceGroupingParenthesis  (
# 36    0      EmptyArgumentList  )
# 36    0      CloseParenOrArgList  )
# 32    2      FunctionCall  (
# 32    2      Selection .
# 31    1      PrefixIncrement  ++
# 31    1      PrefixDecrement  --
# 31    1      FixPoint  +
# 31    1      Negation  -
# 31    1      LogicalNot  !
# 31    1      BitwiseComplement  ~
# 31    1      Indirection  *
# 31    1      AddressOf  &
# 26    2      Multiplication  *
# 26    2      Division  /
# 26    2      Modulo  %
# 24    2      Addition  +
# 24    2      Subtraction  -
# 22    2      BitwiseLeftShift  <<
# 22    2      BitwiseRightShift  >>
# 18    2      LessThan  <
# 18    2      LessOrEqual <=
# 18    2      GreaterThan  >
# 18    2      GreaterOrEqual  >=
# 16    2      EqualEqual  ==
# 16    2      NotEqual  !=
# 14    2      BitwiseAnd  &
# 12    2      BitwiseXor  ^
# 10    2      BitwiseOr  |
# 8     2      ShortCircutAnd  &&
# 6     2      ShortCircutOr  ||
# 5     0      TernaryTest  ?
# 5     3      TernaryChoice  :
# 3     2      Assignment  =
# 3     2      AssignmentAddition  +=
# 0     2      ExpressionSeparator  ,
# 0     2      ArgumentSeparator  ,
