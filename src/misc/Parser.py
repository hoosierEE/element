from Ast import Ast
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
    elif c in cparen:#goto binary
     d.append(NIL); debug('cparen →'); reduce(oparen); x=s.pop(); rp(x);
     break
    elif c.isalnum(): d.append(Ast(c)); break
    elif c in oparen: s.append(Op(c,1))
    elif (not n) or (n in cparen): d.append(Ast(c))
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'↔',n or 'END')
    if   c == semico: 0 if n else d.append(NIL); reduce(oparen); s.append(Op(c,2))
    elif c in cparen:#stay binary
     debug('cparen ↔'); reduce(oparen); x=s.pop(); rp(x)
     continue
    elif c in adverb:
     k = Ast(c,d.pop())#bind adverb func
     if s and s[-1].arity==1 and str(s[-1].name) not in verb:#move left adverb arg to d
      d.append(Ast(s.pop().name))
      s.append(Op(k,2))
     else:
      s.append(Op(Ast(c,d.pop()),1))
    elif c in verb: s.append(Op(c,2))
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

def unit():
 x = """
 input  ‥ expected output
 {x{y}} ‥ (lam (x (lam y)))
 {x(y)} ‥ (lam (x y))
 {(x)y} ‥ (lam (x y))
 {()}   ‥ (lam (lst NIL))
 {()()} ‥ (lam ((lst NIL) (lst NIL)))
        ‥ None
 {[]a}  ‥ (lam (prg NIL) a)
 {[]()} ‥ (lam (prg NIL) (lst NIL))
 abc    ‥ (a (b c))
 """[1:-1].splitlines()[1:]
 m = max(map(len,x))
 for i,o in (map(str.strip,a.split('‥')) for a in x):
  if str(parse(i.strip()))!=o.strip():
   s = f'{i} ⇒ {parse(i)}'
   print(f'{s:<{m}}  expected:{o}')


def test():#(a)b and b(a), symbols
 x = (
  " ab a(b) (a)b" # all same
  " abc a -a --a a-b a-b+c () (a) (a;b) (;b) (a;) (;) (a;;b) a;b ;b a; ; a;;b a+b a++b"
  " [] [x] f[] f[x] f[x;y] f[;y] f[x;] f[;] f[x;;y] a+f[x]"
  " +[] +[x] +[x;y] +[x;y;z] +[;] +[;;]"
  " {} {x} {[]} {[a]} {[]a} {[a]b} {[a];b} {a;b} {ab} {x/y} {{}} {f[x]} {x}y {{x}[x]}"
  " x/y +/y x+/y xf/y (f)/y (+)/y (-a)*b"
  " f//y xf//y (+//)'y x(+/)//'y x(af/)'y"
 ).split()
 m = max(map(len,x))
 for t in x: print(f'{t:<{m}}',end=' ⇒ ');print(parse(t))
