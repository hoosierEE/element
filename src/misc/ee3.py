'''E:E;e|e e:nve|te| t:n|v v:tA|V n:t[E]|(E)|{E}|N'''
from Ast import Ast
S = str.split
Z = lambda x,y:dict(zip(x,y))
bc = S('   (   *   +   -   ; ')
bn = S('  fun mul add sub seq')
bp = Z(bn,(0,  1,  1,  1,  2,)) #{name:precedence}
bt = Z(bc,bn) #{token:name}
uc = S('   (    #    -   ; ')
un = S('  lst count neg nil')
up = Z(un,(0,   1,   1,  1,)) #{name:precedence}
ut = Z(uc,un) #{token:name}
ps = {**bp,**up} #{op:precedence}
pmax = max(ps.values())+1
class ParseError(SyntaxError): pass
def parse(text,verbose=0):
 if not text: return Ast(text)
 t,z,s,d = list(text),len(text),[],[]
 def debug(*args,**kwargs):
  if not verbose: return
  ss,sd = ' '.join(s),' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<25}]',*args,**kwargs)

 def r1(op):
  '''reduce top of stack, merging ";" as needed'''
  if len(d)<(arity:=2-(op in up)): raise ParseError('arity')
  x,k = s.pop(),[d.pop() for _ in range(arity)][::-1]
  debug(f'r1:({x=},{k=})')
  if   x=='lst': x,*k = ('lst',*k[0].children,) if k[0].node=='seq' else k
  elif x=='fun': x,k = k[0],(k[1].children if k[1].node=='seq' else [k[1]])
  elif x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  d.append(Ast(x,*k))

 def reduce_paren():
  '''reduce until matching open paren, then push AST'''
  while s and ps[op:=s[-1]]: r1(op)
  r1(op)

 def reduce(p):
  '''reduce ops with lower precedence (but not parens)'''
  while s and 0<ps[op:=s[-1]]<p: r1(op)

 def balance(op,bal):
  '''raise exception if parens are unbalanced'''
  if   op in '({[': bal.append(')}]'['({['.index(op)])
  elif op in ')}]':
   if not bal or op!=bal.pop(): raise ParseError('unbalanced paren')

 def loop(t,bal):
  '''advance token, alternate unary/binary state'''
  i = 0
  while True:
   while True: #unary
    if i>=z: return
    c = t[i]
    balance(c,bal)
    i += 1
    debug(c,'→')
    if c.isalnum(): d.append(Ast(c))
    elif c==')':
     d.append(Ast('nil'))
     reduce_paren()
    elif c==';':
     d.append(Ast('nil'))
     s.append(bt[c])
     continue
    elif c in uc:
     s.append(ut[c])
     continue
    else: raise ParseError(f'unrecognized token (unary): "{c}"')
    break

   while True: #binary
    if i>=z: return
    c = t[i]
    balance(c,bal)
    i += 1
    debug(c,'↔')
    if c==')':
     reduce_paren()
     continue
    elif c in bc:
     reduce(ps[bt[c]])
     s.append(bt[c])
    else: return debug(f'unrecognized token (binary): "{c}"')
    break

 bal = []
 loop(t,bal)
 if s and s[-1] in bp and len(d)==1: d.append(Ast('nil'))
 reduce(pmax)
 if len(bal): raise ParseError('unbalanaced paren')
 if len(d)!=1: raise ParseError(f'data stack: {d}')
 return d.pop()
