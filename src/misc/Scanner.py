def Scanner(expr:str):
 i,s,z = 0,list(expr),len(expr)
 def peek(): return next(0)
 def next(inc=1):
  nonlocal i
  if i>=z: return ''
  x = s[i]; i += inc; return x
 def tokenize():
  isspace   = lambda:peek()in[*' \t']
  isnumeric = lambda:peek().isnumeric()
  isquote   = lambda:peek()=='"'
  issymbol  = lambda:peek()=='`'
  def namey(x):
   while peek().isalnum(): x += next()
   return x
  def numbery(x):
   while isnumeric(): x += next()
   if peek()=='.':  x += next()
   while isnumeric(): x += next()
   return x
  def stringy(x):
   while i<z and not (isquote() and x[-1]!='\\'): x += next()
   x += next()#add trailing quote
   return x
  def symboly(x):
   if isquote(): return stringy(x+next())
   if peek().isalpha():
    x += next()
    while peek().isalnum(): x += next()
   return x
  def strand(t,f):
   ns = []
   while t():
    ns.append(f(next()))
    while isspace(): next()
   return ns if len(ns)>1 else ns[0]

  ts = []
  while peek():
   if peek()=='\n': ts.append(next())
   elif isspace():
    while isspace(): next()
    ts.append(' ')#compress spaces
   elif isnumeric(): ts.append(strand(isnumeric,numbery))
   elif isquote(): ts.append(strand(isquote,stringy))
   elif issymbol(): ts.append(strand(issymbol,symboly))
   elif peek().isalpha(): ts.append(namey(next()))
   else: ts.append(next())
  return ts
 return tokenize()
