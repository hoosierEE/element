from Ast import Ast
from Parser_test import unit
import collections as C
NIL = Ast('NIL')
Op = C.namedtuple('Op','name arity')
verb = '~!@#$%^&*-_=+|:,.<>?`'
adverb = "'/\\"
oparen = '({['
cparen = ')}]'
semico = ';'
def parse(t:str,verbose:int=0)->Ast:
 if not t: return
 t,z,b,s,d = list(t),len(t),[],[],[]
 def debug(*args):
  if not verbose: return
  ss = ' '.join(f'{repr(Ast(x.name))}‥{x.arity}' for x in s)
  sd = ' '.join(map(str,d))
  print(f'[{ss:<19}] [{sd:<15}]',*args)

 def balance(op):
  if op in oparen: return b.append(cparen[oparen.index(op)])
  if op in cparen and (not b or op!=b.pop()): raise SyntaxError('unbalanced paren')

 def reduce(until:str):
  while s and str(s[-1].name) not in until: r1(s.pop())

 def r1(x:Op):
  k,x = [d.pop() for _ in range(x.arity)][::-1],x.name
  if x==';':
   if k[1].node==x: k = [k[0],*k[1].children]
   if k[0].node==x: k = [*k[0].children,*k[1:]]
  d.append(Ast(x,*k))
  debug('r1')

 def rp(x:Op):#called after reduce(oparen)
  y = (y.children if (y:=d.pop()).node==';' else (y,))
  if   x==Op('[',2): k = Ast('fun',d.pop(),*y)
  elif x==Op('{',3): k = Ast('lam',d.pop(),*y)
  else: k = Ast(x.name,*y)
  if x.name=='(' and len(k.children)==1 and k.children[0]!=NIL: k = k.children[0]
  d.append(k)
  debug('rp')

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'→',n or 'END')
    if   c == semico: [d.append(NIL)for _ in range(-~(not n))]; reduce(oparen); s.append(Op(c,2))
    elif c in cparen:
     d.append(NIL)# comment this, uncomment line 61 to fix adverbs
     debug('cparen →'); reduce(oparen); x=s.pop(); rp(x); break
    elif c in adverb: s.append(Op(Ast(c,Ast(s.pop().name)),1))
    elif c.isalnum() or c in verb: d.append(Ast(c)); break
    elif c in oparen: s.append(Op(c,1))
    elif (not n) or (n in cparen): d.append(Ast(c))
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'↔',n or 'END')
    # if   n in cparen: d.append(NIL)# adverb workaround
    if   c == semico: 0 if n else d.append(NIL); reduce(oparen); s.append(Op(c,2))
    elif c in cparen: debug('cparen ↔'); reduce(oparen); x=s.pop(); rp(x); continue
    # elif n and n in cparen:
    #  d.append(NIL)
    elif c in verb+'[': s.append(Op(c,2))
    elif c in adverb:
     k = Ast(c,d.pop())#bind adverb func
     while n in adverb: k,i,n = Ast(n,k),i+1,t[i+1]if i+1<z else''
     if s and s[-1].arity==1 and str(s[-1].name) not in (verb+oparen):
      d.append(Ast(s.pop().name)); s.append(Op(k,2))
     else: s.append(Op(k,1))
    else:
     if s and d and s[-1].name=='{' and d[-1].node=='[': s.append(Op(';',2))
     else: s.append(Op(d.pop(),1))
     if c.isalnum(): d.append(Ast(c)); continue
     s.append(Op(c,1))
    break

 loop()
 debug('done')
 reduce('')
 while len(d)>1:
  x=d.pop();d.append(Ast(d.pop(),x))
 if len(d)!=1 or len(s) or len(b): return SyntaxError("ERROR: stacks should end up empty")
 return d.pop()
