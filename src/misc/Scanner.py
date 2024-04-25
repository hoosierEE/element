def Scan(expr:str):
 i,s,z = 0,list(expr),len(expr)
 def peek(inc=0): return s[i+inc] if i+inc<z else ''
 def next(): nonlocal i; i += 1; return peek(-1)
 def tokenize():
  isspace   = lambda:peek()in[*' \t']
  isnumeric = lambda:peek().isnumeric() or peek()=='-' and peek(1).isnumeric() and not peek(-1).isalnum()
  isquote   = lambda:peek()=='"'
  issymbol  = lambda:peek()=='`'
  def namey(x):
   while peek().isalnum(): x += next()
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
  def numbery(x):#-?[0-9]+.?[0-9]*
   while peek().isnumeric(): x += next()
   if peek()=='.':    x += next()
   while peek().isnumeric(): x += next()
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
    if peek()=='/':
     while peek() and peek()!='\n': next()
   elif isnumeric(): ts.append(strand(isnumeric,numbery))
   elif isquote(): ts.append(strand(isquote,stringy))
   elif issymbol(): ts.append(strand(issymbol,symboly))
   elif peek().isalpha(): ts.append(namey(next()))
   else: ts.append(next())
  return ts
 return tokenize()
