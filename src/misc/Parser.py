'''
(ab) ⇒ (a b) apply function a to argument b
(+b) ⇒ (+ b) apply function + to argument b
(a+) ⇒ (+ a ∅) + projection waiting for argument ∅
(f/) ⇒ ((/ f) ∅) (/ f) projection awaiting ∅
((a;b)1) ⇒ ((lst a b) 1) apply/index 1 to list
And adverbs:
f/y ⇒ ((/ f) y) 1-argument form
x f/y ⇒ ((/ f) x y) 2-argument form
x f/'y ⇒ ((' (/ f)) x y) multiple adverbs bind together
When parsing "x f/y" left-to-right, "x f" could be (apply x f).
However, once you see "/" it must be the 2-argument adverb ((/ f) x …).
Finally, there are "compositions" and "projections":
(+-) ⇒ (+ (- … …)) (unary + applied to binary - which is waiting on both args)
(1+) ⇒ (+ 2 …) (binary + waiting on an arg (first arg bound to 1))
Compositions can't be just names like (p q) because that's already parsed as (apply p q).

Example: "x y + - z h + g" ⇒ (x (+ y (- (z (+ h g)))))
(∴) t ⇒ [s] [d]
(u) x ⇒ [] [x]
(b) y ⇒ [x:] [y]
(b) + ⇒ [x: +] [y]
(u) - ⇒ [x: + -:] [y]
(u) z ⇒ [x: + -:] [y z]
(b) h ⇒ [x: + -: z:] [y h]
(b) + ⇒ [x: + -: z: +] [y h]
(u) g ⇒ [x: + -: z: +] [y h g]
r     ⇐ [x: + -: z:] [y (+ h g)]
r     ⇐ [x: + -:] [y (z (+ h g))]
r     ⇐ [x: +] [y (- (z (+ h g)))]
r     ⇐ [x:] [(+ y (- (z (+ h g))))]
r     ⇐ [] [(x (+ y (- (z (+ h g)))))]

Example: "xyz" ⇒ (x (y z))
(u) x ⇒ [] [x]
(b) y ⇒ [x:] [y]
(b) z ⇒ [x: y:] [z]
r     ⇐ [x:] [(y z)]
r     ⇐ [] [(x (y z))]

Example: "a(w+x)-b" ⇒ (a (- (+ w x) b))
(u) a ⇒ [] [a]
(b) ( ⇒ [a: ()] []
(u) w ⇒ [a: ()] [w]
(b) + ⇒ [a: () +] [w]
(u) x ⇒ [a: () +] [w x]
rp  ) ⇐ [a:] [(+ w x)]
(b) - ⇒ [a: -] [(+ w x)]
(u) b ⇒ [a: -] [(+ w x) b]
r     ⇐ [a:] [(- (+ w x) b)]
r     ⇐ [] [(a (- (+ w x) b))]

Example: "x(f)/y" ⇒ ((/ f) x y)
(u) x ⇒ [] [x]
(b) ( ⇒ [x: ()] []
(u) f ⇒ [x: ()] [f]
rp  ) ⇒ [x:] [f]
(b) / ⇒ [(/ f)] [x]  SWAP s d; s.push(Ast(/,s.pop()))
(u) y ⇒ [(/ f)] [x y]
r     ⇐ [] [((/ f) x y)]

Example: "f/y" ⇒ ((/ f) y)
(u) f ⇒ [] [f]
(b) / ⇒ [(/ f)] []  SWAP s d; s.push(Ast(/,s.pop()))

Example: "xf/y" ⇒ ((/ f) x y)
(u) x ⇒ [] [x]
(b) f ⇒ [x:] [f]
(b) / ⇒ [(/ f)] [x]
(u) y ⇒ [(/ f)] [x y]
r     ⇐ [] [((/ f) x y)]

'''

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
  ss = ' '.join(f'{x.name}¨{x.arity}' for x in s)#or f'{repr(Ast(x.name))}...'
  sd = ' '.join(map(str,d))
  print(f'[{ss:<19}] [{sd:<15}]',*args)

 def balance(op):
  if op in oparen: return b.append(cparen[oparen.index(op)])
  if op in cparen and (not b or op!=b.pop()): raise SyntaxError('unbalanced paren')

 def reduce(until:str):
  while s and str(s[-1].name) not in until: r1(s.pop())

 def r1(x:Op):#reduce top of stack based on x's arity
  n = 0#number of additional NIL args
  if x.arity>len(d): n = x.arity-len(d)
  k = [d.pop() for _ in range(min(len(d),x.arity))][::-1]+[NIL]*n
  x = x.name
  if x==';':
   if k[1].node==x: k = [k[0],*k[1].children]
   if k[0].node==x: k = [*k[0].children,*k[1:]]
  d.append(Ast(x,*k))
  debug('r1')

 def rp(x:Op):#typical use: reduce(oparen); rp(s.pop())
  y = (y.children if (y:=d.pop()).node==';' else (y,))
  if   x==Op('[',2): k = Ast('fun',d.pop(),*y)
  else: k = Ast(x.name,*y)
  if x.name=='(' and len(k.children)==1 and k.children[0]!=NIL: k = k.children[0]
  d.append(k)
  debug('rp')

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'→',n or 'END')
    if c in semico:
     [d.append(NIL)for _ in(1,1)[len(n):]]; reduce(oparen); s.append(Op(c,2))
    elif c in oparen: s.append(Op(c,1))
    elif c in cparen:
     d.append(NIL); debug('cparen →'); reduce(oparen); x=s.pop(); rp(x);
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: break
    elif c in adverb: x = s.pop(); s.append(Op(Ast(c,Ast(x.name)),x.arity))
    elif c.isalnum(): d.append(Ast(c)); break
    elif (c in verb) and (n in cparen):
     d.append(Ast(c))
     if n in cparen: break
    elif (not n) or (n in cparen): d.append(Ast(c))
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; balance(c); debug(c,'↔',n or 'END')
    if   c == semico: 0 if n else d.append(NIL); reduce(oparen); s.append(Op(c,2))
    elif c in cparen:
     debug('cparen ↔'); reduce(oparen); x=s.pop(); rp(x);
     if not(s and s[-1].name=='{' and x.name=='[' and n!='}'): continue
     else: s.append(Op(';',2))
    elif c in verb+'[': s.append(Op(c,2))
    elif c in adverb:
     k = Ast(c,d.pop())#bind adverb to whatever
     debug('bound',k)
     while n and n in adverb: k,i,n = Ast(n,k),i+1,t[i+1]if i+1<z else''
     debug('adverb',s and s[-1])
     if s:
      if str(s[-1].name) in verb+oparen: s.append(Op(k,1))
      else: d.append(Ast(s.pop().name)); s.append(Op(k,2))
     else: s.append(Op(k,1))
    else:
     s.append(Op(d.pop(),1))
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
