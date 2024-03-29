class Parser:
 '''recursive descent:
 condition = expression ("="|"~"|"<"|">") expression
 expression = ["+"|"-"] term {("+"|"-") term}
 term = factor {("*"|"/") factor}
 factor = ident | number | "(" expression ")"
 '''
 def __init__(s,tokens):
  s.s = tokens
  s.i = 0
  s.z = len(tokens)
 def __repr__(s): return ' '.join(s.s[:s.i]) + '¦' + ' '.join(s.s[s.i:])
 def sym(s): return s.s[s.i] if s.i<s.z else None
 def next(s): s.i += 1
 def accept(s,t):
  if s.sym() == t:
   s.next()
   return 1
  return 0
 def expect(s,t):
  if s.accept(t): return 1
  raise SyntaxError(f'unexpected: {t}')
 def factor(s):
  x = s.sym()
  if x is None: raise SyntaxError(f'factor: {x}')
  if x.isnumeric(): s.next()
  elif x.isalnum(): s.next()
  elif s.accept('('):
   s.expression()
   s.expect(')')
  else: raise SyntaxError(f'factor: {x}')
 def term(s):
  s.factor()
  while s.sym() == '*' or s.sym() == '/':
   s.next()
   s.factor()
 def expression(s):
  if s.sym() == '+' or s.sym() == '-': s.next()
  s.term()
  while s.sym() == '+' or s.sym() == '-':
   s.next()
   s.term()
 def condition(s):
  s.expression()
  if s.i == s.z: return True
  x = s.sym()
  if x and x in '=~<>':
   s.next()
   s.expression()
  else: raise SyntaxError(f'condition: {x}')
 def parse(s):
  try: s.condition()
  except SyntaxError as e:
   print(e.msg)
   return False
  return s.i == s.z
