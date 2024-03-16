class Scanner:
 ''' -a2+b3*51a*-5 => [- a2 + b3 * 51 a * - 5] '''
 def __init__(s,expr:str):
  s.s = [*expr] # individual characters
  s.i = 0 # current index
  s.z = len(expr)
  s.tokens = s.tokenize()
  assert len(expr) == sum(map(len,s.tokens)), 'wat happen'
 def peek(s): return s.next(0)
 def next(s,inc=1):
  if s.i>=s.z: return ''
  x = s.s[s.i]
  s.i += inc
  return x
 def tokenize(s):
  ts = []
  while s.peek():
   t = '' # current token
   if s.peek().isnumeric(): # [0-9]+ not followed by [A-Za-z]
    while s.peek().isnumeric(): t += s.next()
    ts.append(t)
    if s.peek().isalpha(): raise NameError("Numbers can't have letters in them.")
   elif s.peek().isalpha(): # [A-Za-z][0-9A-Za-z]*
    while s.peek().isalnum(): t += s.next()
    ts.append(t)
   else: ts.append(s.next())
  return ts
