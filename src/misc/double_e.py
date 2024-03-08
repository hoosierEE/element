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
 '+': (10,2,'plus'),
 '-': (10,2,'minus'),
 '*': (20,2,'times'),
 '/': (20,2,'divide'),
 '^': (30,2,'power'),
 '=': (40,2,'equal'),
 '[': ( 0,2,'['),
 ']': (50,2,']'),
}
uop = {
 '-': (10,1,'negate'),
 '*': (10,1,'first'),
 '=': (10,1,'group'),
}

def bp(state:str,op:str) -> (int,str):
 return {'binary':bop, 'unary':uop}[state].get(op,(0,'unknown operator'))

##               -      *     =     +    -     *     /      ^     =     [ ] f[]
Op = Enum('Ops','negate first group plus minus times divide power equal l r fun')
class Parser:
 def __init__(s,tokens):
  s.state = 'unary'
  s.s = tokens
  s.o = [] # operators
  s.d = [] # data/operands
  s.i = 0
  s.z = len(tokens)
 def __repr__(s): return ' '.join(s.s[:s.i]) + '¦' + ' '.join(s.s[s.i:])
 def peek(s): return s.next(0)
 def end(s): return s.i >= s.z
 def next(s,inc=1):
  if s.end():
   return None
  x = s.s[s.i]
  s.i += inc
  return x

 def reduce(s,op,*until):
  '''
  Make AST for expr on stacks while bp(s.o.top()) > bp.
  Ast(s.o.top(), nargs())
  Pop operator from s.o (and as many operands as it needs from s.d) and build Ast
  '''
  top = s.o[-1] # top of operator stack

 def unary(s):
  op = s.peek()
  match op:
   case '[': s.o.append('[')
   case '-'|'='|'*': s.o.append(op)
   case _:
    s.d.append(Ast(uop[op]))
    s.state = 'binary'

 def binary(s):
  op = s.peek()
  match op:
   case '[':
    s.reduce(op)
    s.o.append(op,'fun')
   case '+'|'-'|'*'|'/'|'^'|'=':
    s.reduce(op)
    s.state = 'unary'
   case ']':
    s.reduce(op,'[','fun') # reduce until matching grouping paren or function call operand
    if s.o[-1] == 'fun':
     args = s.d[]
     s.d.append(Ast(op, ))


class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  if not s.children: return f'{s.node}'
  return f'({s.node} {" ".join(map(repr,s.children))})'


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
