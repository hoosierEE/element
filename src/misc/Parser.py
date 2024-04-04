from Ast import Ast
from collections import namedtuple
NIL = Ast('NIL')
Op = namedtuple('Op','name arity')
adverb = "'/\\"
oparen = '({['
cparen = ')}]'
semico = ';'
lookup = {
 Op('{',1): 'lam',
 Op('{',2): 'lam',
 Op('(',1): 'list',
 Op('(',2): 'apply',
 Op('[',1): 'progn',
 Op('[',2): 'call',
 Op(';',2): 'seq',
}
def parse(text,verbose=0):
 if not text: return
 t,z,b,s,d = list(text),len(text),[],[],[]
 def debug(*args):
  if not verbose: return
  ss = ' '.join(f'{lookup.get(x,x.name)}({x.arity})' for x in s)
  sd = ' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<25}]',*args)

 def balance(op):
  if op in oparen: return b.append(cparen[oparen.index(op)])
  if op in cparen and (not b or op!=b.pop()): raise SyntaxError('unbalanced paren')

 def r1(op,m='r1'):
  if not s: return
  x,k = s.pop(),[d.pop() for _ in range(op.arity)][::-1]
  x = lookup.get(x,x.name)
  if x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  elif x=='list': x,*k = (x,*k[0].children,) if k[0].node=='seq' else k
  debug(f'{m}:({x},{k})')
  d.append(Ast(x,*k))

 def reduce(until):
  while s and s[-1].name not in oparen+cparen+until:
   r1(s[-1],'r')

 def reduce_paren():#reduce everything up to open paren; push AST
  while s and (op:=s[-1]).name not in oparen: r1(op,'rp')
  r1(op,'rp')

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return d.append(NIL)
    c = t[i]
    i += 1
    balance(c)
    debug(c,'→')
    if c==semico:
     d.append(NIL)
     s.append(Op(c,2))
    elif c in cparen:
     d.append(NIL)
     reduce_paren()
     break
    elif c.isalnum():
     d.append(Ast(c))
     break
    elif c in adverb:
     s.append(Op(s.pop().name+c,2))
    else:
     s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c = t[i]
    i += 1
    balance(c)
    debug(c,'↔')
    if c in cparen:
     reduce_paren()
     if i<z and t[i] in adverb:
      break
    elif c in semico:
     reduce(c)
     s.append(Op(c,2))
     break
    elif c in oparen:
     s.append(Op(c,1))#-(c!='[')))
     break
    elif c in adverb:
     while i<z and t[i] in adverb:
      c += t[i]
      i += 1
     s.append(Op(repr(d.pop())+c,1))
     break
    else:
     s.append(Op(c,2+(c in adverb)))
     break

 loop()
 debug('done')
 reduce('')
 r = d.pop()
 if len(d): print("ERROR: data stack should be empty")
 if len(s): print("ERROR: operator stack should be empty")
 return r
