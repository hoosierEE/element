class Scanner:
 '''
 Strands of (number|string|symbol) become lists.
 Multiple spaces become one space.
 "1" ⇒ ["1"]
 "1 2+3 4 5" ⇒ [["1","2"],"+",["3","4","5"]]
 '2+"hello world"' ⇒ ["2","+","hello world"]
 "2+``a2.95" ⇒ ["2","+",["`","`a2"],".","95"]
 '''
 def __init__(s,expr:str):
  s.s,s.i,s.z = list(expr),0,len(expr)
  s.t = s.tokenize()
 def peek(s): return s.next(0)
 def next(s,inc=1):
  if s.i>=s.z: return''
  x = s.s[s.i]; s.i += inc; return x

 def tokenize(s):
  isnumeric = lambda:s.peek().isnumeric()
  isspace   = lambda:s.peek().isspace()
  isquote   = lambda:s.peek()=='"'
  issymbol  = lambda:s.peek()=='`'
  def namey(x):
   while s.peek().isalnum(): x += s.next()
   return x
  def numbery(x):
   while isnumeric(): x += s.next()
   if s.peek()=='.':  x += s.next()
   while isnumeric(): x += s.next()
   return x
  def stringy(x):
   while s.i<s.z and not (isquote() and x[-1]!='\\'): x += s.next()
   x += s.next()#add trailing quote
   return x
  def symboly(x):
   if isquote(): return stringy(x+s.next())
   if s.peek().isalpha():
    x += s.next()
    while s.peek().isalnum(): x += s.next()
   return x
  def strand(t,f):
   ns = []
   while t():
    ns.append(f(s.next()))
    while isspace(): s.next()
   return ns if len(ns)>1 else ns[0]

  ts = []
  while s.peek():
   if s.peek().isspace():
    while s.peek().isspace(): s.next()
    ts.append(' ')#compress spaces
   elif isnumeric(): ts.append(strand(isnumeric,numbery))
   elif isquote(): ts.append(strand(isquote,stringy))
   elif issymbol(): ts.append(strand(issymbol,symboly))
   elif s.peek().isalpha(): ts.append(namey(s.next()))
   else: ts.append(s.next())
  return ts
