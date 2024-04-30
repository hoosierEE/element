from typing import List,Tuple
def Scan(expr:str)->List[str|Tuple[str]]:
 '''
 Scan(str) ⇒ List[str|Tuple[str]]
 Scan turns a string into a list of tokens.
 The resulting list is either bare strings,
 or "strands" of same-type values represented as tuples.
 examples:
  "x+1"            ⇒ ["x", "+", "1"]
  "1 2 3"          ⇒ [("1", "2", "3")]
  "foo[x];`ax``by" ⇒ ["foo", "[", "x", "]", ";", ("`ax", "`", "`by")]
  '`"hi"`world'    ⇒ [('`"hi"', '`world')]
  '"hi""world"'    ⇒ [("hi", "world")]
 Numeric strands are numbers separated by spaces.
 Spaces are optional for symbol or string strands.
 Detect syntax errors: '2a', unclosed quote
 '''
 i,s,z = 0,list(expr),len(expr)
 def peek(inc=0): return s[i+inc] if 0<=i+inc<z else ''
 def next(): nonlocal i;i+=1;return peek(-1)
 def err(m,LF='\n'): return f'Syntax: {m}{LF}{(expr[:i]+peek()).strip()}'
 def tokenize():
  isspace   = lambda:peek()in[*' \t']
  isnegnum  = lambda:peek()=='-' and peek(1).isnumeric() and peek(-1) not in [*'.0123456789']
  isnumeric = lambda:peek().isnumeric() or isnegnum()
  isquote   = lambda:peek()=='"'
  issymbol  = lambda:peek()=='`'
  def namey(x):
   while peek().isalnum(): x += next()
   return x
  def stringy(x):
   while i<z and not (isquote() and x[-1]!='\\'): x += next()
   if not isquote(): raise SyntaxError(err('unterminated quote'))
   x += next()#add trailing quote
   return x
  def symboly(x):
   if isquote(): return stringy(x+next())
   if peek().isalpha():
    x += next()
    while peek().isalnum(): x += next()
   return x
  def numbery(x):#-?[0-9]+.?[0-9]*
   while peek().isnumeric() and not peek(1).isalpha(): x += next()
   dot=0
   if peek()=='.': dot=1; x += next()
   while peek().isnumeric(): x += next()
   if peek().isalpha() and not dot: raise SyntaxError(err('numbers can not contain letters'))
   return x
  def strand(t,f):#stranding for symbols, strings, and numbers
   ns = ()
   while t():
    ns = (*ns, f(next()))
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
 try: return tokenize()
 except SyntaxError as e: print(e)
