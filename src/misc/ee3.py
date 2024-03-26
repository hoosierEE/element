from Ast import Ast
from inspect import currentframe
S = str.split
Z = lambda x,y:dict(zip(x,y))
lineno = lambda:str(currentframe().f_back.f_lineno)
class ParseError(SyntaxError): pass

bo = S('   (   *   +    -  ; ')
bn = S('  fun mul add sub seq')
bp = Z(bn,(3,  2,  2,  2,  3,))
bt = Z(bo,bn) # {token:name}
uo = S('   (    #    - ')
un = S('  lst count neg')
up = Z(un,(3,   2,   2,))
ut = Z(uo,un) # {token:name}
ps = {**bp,**up,'prj':3} # {op:precedence}
pmax = max(ps.values())+1

def parse(text):
 t,z,s,d = list(text),len(text),[],[]

 def debug(*args,**kwargs):
  ss = ' '.join(s)
  sd = ' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<20}]',*args,**kwargs)

 def rtop(arity):
  x,k = s.pop(),[d.pop() for _ in range(arity)][::-1]
  debug('rtop:',x)
  if x=='lst':
   print('LST')
   return d.append(Ast(x,*k[0].children))
  if x=='fun': x,*k = k
  if x=='seq':
   print('SEQ')
   k = [*(k[0].children if k[0].node==x else [k[0]]),*(k[1].children if k[1].node==x else [k[1]])]
  d.append(Ast(x,*k))

 def rp():
  while s:
   debug('rp')
   if op:=s[-1] in ('fun','lst'): break
   reduce(pmax)

 def reduce(p):
  while s:
   if ps[op:=s[-1]]>=p: break
   if len(d)<(arity:=2-(op in un)): raise ParseError('arity')
   rtop(arity)

 def loop(t):
  i = 0
  while True:
   while True: # unary
    if i>=z: raise ParseError('end of tokens')
    op = t[i]
    i += 1
    debug(op,'unary')
    if op.isalnum():
     d.append(Ast(op))
     break
    elif op in uo:
     reduce(ps[name:=ut[op]])
     s.append(name)
     continue
    else: raise ParseError(f'unrecognized token (unary): "{op}"')
    break

   while True: # binary
    if i>=z: return # end of tokens
    op = t[i]
    i += 1
    debug(op,'binary')
    if op==')':
     rp()
     continue
    elif op in bo:
     name = bt[op]
     reduce(ps[name])
     s.append(name)
    else:
     debug(f'unrecognized token (binary): "{op}"')
     return
    break

 loop(t)
 debug('final')
 reduce(pmax)
 return d.pop()
