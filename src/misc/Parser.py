from collections import namedtuple
from Ast import Ast
NIL = Ast('NIL')
Op = namedtuple('Op','name arity')
adverb = "'/\\"
oparen = '({['
cparen = ')}]'
semico = ';'
lookup = {
 Op('{',1):'lam',#{x+y}/z
 Op('{',2):'lam',#n{x+y}/z
 Op('(',1):'list',#or to override precedence: (-a)+b
 Op('(',2):'list',#n(x) as in n(|+\)\1 1
 Op('[',1):'progn',#[x+1;y] ⇒ y
 Op('[',2):'call',#f[x]
 Op(';',2):'seq',#x;y
}
def parse(t,verbose=0):
 if not t: return
 t,z,b,s,d = list(t),len(t),[],[],[]
 def debug(*args):
  if not verbose: return
  ss = ' '.join(f'{lookup.get(x,x.name)}.{x.arity}' for x in s)
  sd = ' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<25}]',*args)

 def balance(op):
  if op in oparen: return b.append(cparen[oparen.index(op)])
  if op in cparen and (not b or op!=b.pop()): raise SyntaxError('unbalanced paren')

 def r1(x):
  k = [d.pop() for _ in range(x.arity)][::-1]
  x = lookup.get(x,x.name)
  if   x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  elif x=='list': x,*k = (x,*k[0].children,) if k[0].node=='seq' else k
  d.append(Ast(x,*k))
  debug('r1')

 def reduce(until):
  while s and s[-1].name not in until: r1(s.pop())

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return d.append(NIL)
    c,i = t[i],i+1; balance(c); debug(c,'→')
    if   c in semico: d.append(NIL); s.append(Op(c,2))
    elif c in cparen: d.append(NIL); reduce(oparen); r1(s.pop()); break
    elif c in oparen: s.append(Op(c,1))
    elif c in adverb:
     while i<z and t[i] in adverb: c,i = c+t[i],i+1
     if s and s[-1].name=='bind': s.pop(); s.append(Op(c,3))
     else: s.append(Op(c,2))
    elif c.isalnum() or i<z and t[i] in adverb: d.append(Ast(c)); break
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i = t[i],i+1; balance(c); debug(c,'↔')
    if   c in cparen: reduce(oparen); r1(s.pop()); continue
    elif c in "{(": s.append(Op('bind',1)); s.append(Op(c,1))
    elif c in adverb:
     while i<z and t[i] in adverb: c,i = c+t[i],i+1
     if s and s[-1].name=='bind': s.pop(); s.append(Op(c,3))
     else: s.append(Op(c,2))
    else:
     if i<z and t[i] in adverb: s.append(Op('bind',1)); d.append(Ast(c))
     else: s.append(Op(c,2))
    break

 loop()
 debug('done')
 reduce('')
 r = d.pop()
 if len(d) or len(s): raise SyntaxError("ERROR: stacks should end up empty")
 return r

def test():#TODO:juxtaposition:  (a)b and b(a), symbols
 x = (
  " a -a --a aa aaa a-b a-b+c (a) (a;b) (;b) (a;) (;) (a;;b) a;b ;b a; ; a;;b a+b a++b"
  " [] [x] f[] f[x] f[x;y] f[;y] f[x;] f[;] f[x;;y] a+f[x]"
  " x/y +/y x+/y xf/y (f)/y (+)/y (-a)*b"
  " f//y xf//y (+//)'y x(+/)//'y x(af/)'y").split()
 m = max(map(len,x))
 for t in x: print(f'{t:<{m}} ⇒ {parse(t)}')
if __name__=='__main__': test()
