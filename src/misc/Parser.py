from collections import namedtuple
from Ast import Ast
NIL = Ast('NIL')
Op = namedtuple('Op','name arity')
lookup = {
 ('{',1):'lam',#{x+y}/z
 ('{',2):'lam',#n{x+y}/z
 ('(',1):'lst',#or to override precedence: (-a)+b
 ('(',2):'lst',#n(x) as in n(|+\)\1 1
 ('[',1):'prg',#[x+1;y] ⇒ y
 ('[',2):'fun',#f[x]
 (';',2):'seq',#x;y
}
adverb = "'/\\"
oparen = '({['
cparen = ')}]'
semico = ';'
def parse(t,verbose=0):
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

 def reduce(until):
  while s and str(s[-1].name) not in until:
   r1(s.pop())

 def r1(x):
  k,x = [d.pop() for _ in range(x.arity)][::-1],x.name
  if x==';':
   if k[1].node==x: k = [k[0],*k[1].children]
   if k[0].node==x: k = [*k[0].children,*k[1:]]
  d.append(Ast(x,*k))
  debug('r1')

 def rp(x):#called after reduce(oparen)
  x,y = lookup[x],d.pop()
  y = (y.children if y.node==';' else (y,))
  k = Ast(x,*((d.pop(),) if x=='fun' else ()),*y)
  d.append(k.children[0] if x=='lst'and len(k.children)==1 else k)
  debug('rp')

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'→',n or 'END')
    if   c == semico and not n: d.append(NIL)
    if   c == semico: d.append(NIL); reduce(oparen); s.append(Op(c,2))
    elif c in cparen: d.append(NIL); debug('test'); reduce(oparen); rp(s.pop()); break
    elif c.isalnum(): d.append(Ast(c)); break
    elif c in oparen: s.append(Op(c,1));
    elif (not n) or (n and n in cparen): d.append(Ast(c))
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'↔',n or 'END')
    if   c == semico and not n: d.append(NIL)
    if   c == semico: reduce(oparen); s.append(Op(c,2))
    elif c in cparen: reduce(oparen); rp(s.pop()); continue
    elif c in adverb: s.append(Op(Ast(c,d.pop()),1))
    elif c.isalnum(): s.append(Op(repr(d.pop()),1)); d.append(Ast(c)); continue
    else: s.append(Op(c,2))
    break

 loop()
 debug('done')
 reduce([])
 while len(d)>1:
  x=d.pop();d.append(Ast(d.pop(),x))
 if len(d)!=1 or len(s) or len(b): return SyntaxError("ERROR: stacks should end up empty")
 return d.pop()

def test():#TODO:juxtaposition:  (a)b and b(a), symbols
 x = (
  " ab a(b) (a)b abc"
  " a -a --a a-b a-b+c (a) (a;b) (;b) (a;) (;) (a;;b) a;b ;b a; ; a;;b a+b a++b"
  " [] [x] f[] f[x] f[x;y] f[;y] f[x;] f[;] f[x;;y] a+f[x]"
  " x/y +/y x+/y xf/y (f)/y (+)/y (-a)*b"
  " f//y xf//y (+//)'y x(+/)//'y x(af/)'y"
 ).split()
 m = max(map(len,x))
 for t in x:
  print(f'{t:<{m}} ⇒ ',end='');print(parse(t))
