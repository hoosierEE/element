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
