# https://erikeidt.github.io/The-Double-E-Method
# recursive descent parsing for statements, blocks, and expressions
class Scanner:
 ''' -a2+b3*51a => [- a2 + b3 * 51 a] '''
 def __init__(s,expr):
  s.s = [*expr]
  s.i = 0
  s.z = len(expr)
  s.tokens = s.tokenize()
  assert len(expr) == sum(map(len,s.tokens)), 'wat happen'
 def tokenize(s):
  ts = []
  while s.peek():
   t = ''
   if s.peek().isnumeric(): # [0-9]+ not followed by [A-Za-z]
    while s.peek().isnumeric():
     t += s.next()
    ts.append(t)
    if s.peek().isalpha():
     raise NameError("Numbers can't have letters in them.")
   elif s.peek().isalpha(): # [A-Za-z][0-9A-Za-z]*
    while s.peek().isalnum():
     t += s.next()
    ts.append(t)
   else: # 1-char non-alphanumeric symbol
    ts.append(s.next())
  return ts
 def peek(s): return s.next(0)
 def next(s,inc=1):
  if s.i>=s.z:
   return ''
  x = s.s[s.i]
  s.i += inc
  return x


bop = { #{token : (bp, arity, name)}
 '+': (20,2,'add'),
 '-': (20,2,'sub'),
 '*': (30,2,'mul'),
 '/': (30,2,'div'),
 '^': (40,2,'pow'),
 '=': (50,2,'equal'),
 '[': (91,2,'fun'), # funcall (arity=2): (f: function name, [..]: argument list)
 ']': (90,0,'end_group'),
}
uop = {
 '-': (20,1,'negate'),
 '*': (20,1,'first'),
 '=': (20,1,'group'),
 '[': (92,0,'begin_group'), # start group
 ']': (90,0,'empty_arglist'), # emtpy argument list
}
fns = {
 'inc':  (10, 1, 'inc/1'), # def inc(x): return add2(x,1)
 'add2': (10, 2, 'add/2'), # def add2(x,y): return x+y
 'sub2': (10, 2, 'sub/2'), # def sub2(x,y): return x-y
 'add3': (10, 3, 'add/3'), # def add3(x,y,z): return x+y+z
}


class Parser:
 def __init__(s,tokens):
  s.state = 'unary' # current state
  s.o = [] # operator stack [(bp,arity,description)]
  s.d = [] # Ast
  s.s = tokens
  s.i = 0 # current token pointer
  s.z = len(tokens)
 def __repr__(s):
  return ' '.join(s.s[:s.i])+'¦'+' '.join(s.s[s.i:])
 def top(s): return s.o[-1] if s.o else None
 def done(s): s.state = 'done'
 def err(s): s.state = 'error'
 def end(s): return s.i >= s.z
 def next(s,inc=1) -> str|None:
  if s.i<s.z:
   x = s.s[s.i]
   s.i += inc
   return x

 def reduce(s,lbp):
  while s.o and lbp <= s.o[-1][0]:
   _,arity,desc = s.o.pop()
   if len(s.d) < arity: return s.err()
   operands = [s.d.pop() for _ in range(arity)]
   s.d.append(Ast(desc,*operands))

 def reduce_until(s,*matches):
  while s.o and s.top() not in matches:
   print('reduce_until')
   step(s)
   _,arity,desc = s.o.pop()
   operands = [s.d.pop() for _ in range(arity)]
   s.d.append(Ast(desc,*operands))

  s.err()

 def unary(s):
  if (op := s.next()).isalnum():
   s.d.append(Ast(op))
   s.state = 'binary'
  elif op in uop: s.o.append(uop[op])
  elif op is None: s.done()
  else: s.err()

 def binary(s):
  if (op := s.next()) == '[': # function call
   s.reduce(bop[op][0])
   s.o.append(bop[op])
   s.state = 'unary'
  elif op == ']': # could be funcall or close paren
   s.reduce_until(bop['['],uop['['])
   _,arity,desc = s.top()
   if desc == 'fun':
    s.o.pop()
    fname,*args = [s.d.pop() for _ in range(arity)][::-1]
    s.d.append(Ast(fname,*args))
  elif op in bop:
   s.reduce(bop[op][0])
   s.o.append(bop[op])
   s.state = 'unary'
  elif op is None:
   s.done()
  else:
   s.err()

 def parse(s):
  while True:
   step(s)
   if s.state == 'unary': s.unary()
   elif s.state == 'binary': s.binary()
   else: break
  s.reduce(0) # finish up
  return {'state':s.state, 'ast':s.d}


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  if not s.children: return f'{s.node}'
  return f'({s.node} {" ".join(map(repr,s.children))})'


def step(p):
 print(f'[{" ".join(x[2] for x in p.o)}]  --  {p.d}  --  "{"fin" if p.end() else p.s[p.i]}" ({p.state})')


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
  print('ERROR: should have raised')
 except NameError:
  pass

 assert all(Parser(Scanner(x).tokens).parse()
            for x in ['2', '-2', 'a', 'a-a', '-a*b+c', '-a<3'])
 assert any(not Parser(Scanner(x).tokens).parse()
            for x in ['-', '-+', '+', 'a-'])
 print('all good')

if __name__ == "__main__":
 test()

# bp    arity  operator
# 36    0      PrecedenceGroupingParenthesis  (
# 32    2      FunctionCall  (
# 36    0      EmptyArgumentList  )
# 36    0      CloseParenOrArgList  )
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
# 20    2      Order <=>
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
# 3     2      AssignmentMultiplication  *=
# 3     2      AssignmentDivision  /=
# 3     2      AssignmentModulo  %=
# 3     2      AssignmentAddition  +=
# 3     2      AssignmentSubtraction  -=
# 3     2      AssignmentBitwiseAnd  &=
# 3     2      AssignmentBitwiseXor  ^=
# 3     2      AssignmentBitwiseOr  |=
# 3     2      AssignmentBitwiseLeftShift  <<=
# 3     2      AssignmentBitwiseRightShift  >>=
# 0     2      ExpressionSeparator  ,
# 0     2      ArgumentSeparator  ,
