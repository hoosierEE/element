class Lexer:
 def __init__(self,s):
  self.s = []
  self.i = 0
  N = len(s)
  i = 0
  while i<N:
   n = '' # numbers
   while i<N and s[i].isnumeric():
    n += s[i]
    i += 1
   if len(n):
    self.s.append({'type':'NUM','match':n})
    continue
   n = '' # ids
   while i<N and s[i].isalpha():
    n += s[i]
    i += 1
   if len(n):
    self.s.append({'type':'ID','match':n})
    continue
   # operators
   self.s.append({'type':s[i],'match':s[i]})
   i += 1

 def next(self):
  self.i += 1
  return self.s[self.i]

 def peek(self): return self.s[self.i]
 def expect(self,t): assert self.s[self.i]['match'] == t

def parse(): ...
def test():
 lexer = Lexer('(999+2)*3')
 BPS = {"":0,'NUM':0,'ID':0,')':0,'+':20,'-':20,'*':30,'/':30,'^':40,'(':50,}
 NUDS = {
  'NUM': lambda t: float(t['match']),
  'ID': lambda t: t['match'],
  '+': lambda t,bp: parse(bp),
  '-': lambda t,bp: {'type':'neg', 'value':parse(bp)},
  '(': lambda: parse() if lexer.expect(')') else None,
 }
 LEDS = {'+': lambda left,t,bp: {'type':'+', },}
test()
