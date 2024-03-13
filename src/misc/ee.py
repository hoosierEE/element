# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
from Scanner import Scanner

debug = print
# def debug(*args,**kwargs): pass

bop = { #{token : (bp, arity, name)}
 '+': (30,2,'add'),
 '-': (30,2,'sub'),
 '*': (30,2,'mul'),
 '%': (30,2,'div'),
 '^': (30,2,'pow'),
 '=': (30,2,'equal'),
 '[': (98,2,'fun'), # funcall (arity=2): (f: function name, [..]: argument list)
 ']': (99,0,'arglist'),
 ')': (99,0,'cparen'),
 ';': (90,2,'semi'),
}

uop = {
 '-': (30,1,'negate'),
 '*': (30,1,'first'),
 '+': (30,1,'flip'),
 '=': (30,1,'group'),
 '%': (30,1,'sqrt'),
 '(': (99,0,'list'), # start group
 ']': (99,0,'empty_arglist'), # emtpy argument list
}

fns = {
 'inc':  (20,1,'inc/1'), # def inc(x): return add2(x,1)
 'add2': (20,2,'add/2'), # def add2(x,y): return x+y
 'sub2': (20,2,'sub/2'), # def sub2(x,y): return x-y
 'add3': (20,3,'add/3'), # def add3(x,y,z): return x+y+z
}


class Parser:
 def __init__(s,tokens):
  s.state = 'unary' # current state
  s.o = [] # operator stack [(bp,arity,description)]
  s.d = [] # Ast
  s.s = tokens # [::-1]
  s.i = 0 # current token pointer
  s.z = len(tokens)
 def __repr__(s): # return ' '.join(s.s[:s.i])+'¦'+' '.join(s.s[s.i:])
  o = ' '.join(x[2] for x in s.o)
  d = ' '.join(map(repr,s.d))
  t = f'«{s.state}»'
  return f'{s.s[s.i] if s.i<s.z else " ":<5} • {o:<20} • {d:<20} {t}'
 def top(s): return s.o[-1] if s.o else None
 def setstate(s,newstate,msg=''):
  if msg: debug(msg)
  if s.state in ('done','error'): return
  s.state = newstate
 def end(s): return s.i >= s.z
 def next(s,inc=1) -> str|None:
  if s.i<s.z: x=s.s[s.i]; s.i+=inc; return x

 def reduce_until(s,*matches):
  while s.top() not in matches:
   debug('(until)',s)
   if not s.o:
    return s.setstate('error')
   op,arity,name = s.o.pop()
   args = [s.d.pop() for _ in range(arity)]
   s.d.append(Ast(name,*(args[::-1])))

 def reduce(s,bp):
  while s.o:
   debug(s)
   p,arity,name = s.top()
   if p >= bp:
    break
   # FIXME: fun should pop argument name and argument list
   # Currently, we put the argument name on the stack,
   # but the argument list should have already been reduced to
   # (semi arg1 arg2 ... argN) so it looks like a single argument
   if len(s.d) < arity:
    return s.setstate('error',"'parse ERROR: not enough arguments on data stack")
   s.o.pop() # discard top (previous s.top() provided all we need)
   s.d.append(Ast(name,*[s.d.pop() for _ in range(arity)][::-1]))

 def unary(s):
  op = s.next()
  while op and op.isspace(): op = s.next()
  if op is None: return s.setstate('done')
  if op.isnumeric():
   nums = [Ast(op)]
   while (op := s.next()):
    if op.isspace(): continue
    if op.isnumeric(): nums.append(Ast(op))
    else: s.i-=1; break
   s.d.append(Ast('array',*nums) if len(nums)>1 else Ast(*nums))
   s.setstate('binary')
  elif op.isalnum(): # name
   s.d.append(Ast(op))
   s.setstate('binary')
  elif op in uop: s.o.append(uop[op])
  else: s.setstate('error')

 def binary(s):
  op = s.next()
  while op and op.isspace(): op = s.next()
  if op is None: return s.setstate('done')

  if op == '[': # in binary state, '[' means function call
   fn = s.d.pop().node # function name
   s.reduce(bop[op][0])
   s.o.append(fns[fn]) # push func to op stack
   s.o.append(bop[op]) # show reduce_until where to stop
   s.setstate('unary')

  elif op == ']':
   s.reduce(bop[op][0])
   # s.reduce_until(bop['['])
   # args = s.d.pop()
   # tmp = []
   # while args.node == 'semi':
   #  first,args = args.children
   #  tmp.append(first)
   # if tmp:
   #  s.d.append(Ast(s.o.pop()[2],*(tmp+[args])))
   # else:
   #  s.d.append(Ast(s.o.pop()[2],args))
   # s.setstate('binary')
   s.d.append(Ast(s.o.pop()[-1],s.d.pop()))
   s.setstate('binary')

  elif op == ')':
   s.reduce_until(uop['('])
   args = s.d.pop()
   tmp = []
   while args.node == 'semi':
    first,args = args.children
    tmp.append(first)
   if tmp:
    s.d.append(Ast(s.o.pop()[2],*(tmp+[args])))
   else:
    s.d.append(Ast(s.o.pop()[2],args))
   s.setstate('binary')

  elif op in bop:
   s.reduce(bop[op][0])
   s.o.append(bop[op])
   s.setstate('unary')

  else:
   s.setstate('error')

 def parse(s):
  while True:
   if s.state == 'unary': debug(s); s.unary()
   elif s.state == 'binary': debug(s); s.binary()
   else: break
  if s.state == 'done': s.reduce(100)
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
