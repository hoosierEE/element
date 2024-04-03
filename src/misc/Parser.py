from Ast import Ast
from collections import namedtuple
NIL = Ast('NIL')
Op = namedtuple('Op','name arity')
adverb = "'/\\"
oparen = '({['
cparen = ')}]'
semico = ';'
lookup = {
 Op('{',1): 'lambda',
 Op('{',2): 'lambda2',
 Op('(',1): 'list',
 Op('(',2): 'projection',
 Op('[',1): 'progn',
 Op('(',2): 'call',
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
  if x=='list': x,*k = (x,*k[0].children) if k[0].node=='seq' else k
  if x=='seq' and k[1].node=='seq': k = [k[0],*k[1].children]
  debug(f'{m}:({x},{k})')
  d.append(Ast(x,*k))

 def reduce(until):
  while s and s[-1]!=until: r1(s[-1])

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
     op = s.pop()
     s.append(Op(op.name+c,op.arity))
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
    elif c==semico:
     reduce(Op(c,2))
     s.append(Op(c,2))
     break
    elif c in adverb:
     dat = d.pop()
     print(dat.node,dat.children)
     s.append(Op(dat+c,1))
     break
    else:
     s.append(Op(c,2))
     break

 loop()
 debug('done')
 reduce(Op('',0))
 r = d.pop()
 assert not len(d),"data stack should be empty"
 assert not len(s),"operator stack should be empty"
 return r
