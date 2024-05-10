# TODO: simplify (prototype only)
# get rid of integers
# don't save type info; instead compute it on-demand
# use plain Python values instead of Val class
from Ast import Ast
from Builtin import ASSIGN,VERB
from Semantic import lamp,formalize
class Sym(str):pass
class Name(str):pass
class Num(float):pass
Ty = dict(zip((tuple,int,float,Num,str,Name,Ast),
              'l     i   f     d   s   n    a'.split()))
# TG = {int:'d',float:'d',**Ty}#generic Num mapping
Yt = {v:k for k,v in Ty.items()}

class K:
 def __init__(s,v:str):
  s.t: type   = tty(v) if type(v)==tuple else Ty[ty(v)]
  s.v: object = tuple(map(Yt[s.t.lower()],v)) if s.t.isupper() else Yt[s.t](v)

 def __getitem__(s,k):
  return s.v[k]

 def __repr__(s):
  return f'{s.v}:{s.t}'


def tty(xs:tuple) -> type:
 t = {ty(x) for x in xs}
 return Ty[t.pop()].upper() if len(t)==1 else 'L'

def isnumeric(x:str) -> bool:
 return x.replace('.','').replace('-','').isnumeric()

def ty(x:str) -> type:
 match x:
  case str():
   if x[0] in '"`': return (str,Sym)[x[0]=='`']
   if isnumeric(x): return float if '.' in x else int
   return Name
  case K(): return x.t
  case _: return type(x)

def v1(op,x): return f'{op}:{x}'
def v2(op,x,y):
 match op,ty(x),ty(y):
  case ['-',tuple(),tuple()]: return tuple(v2(op,a,b) for a,b in zip(x,y))
  case ['-',tuple(),float()]: return tuple(a-float(y) for a in x)
  case ['-',float(),tuple()]: return tuple(float(x)-b for b in y)
  case ['-',float(),float()]: return x-y
  case [',',tuple(),tuple()]: return (*x,*y)
  case [',',tuple(),_]: return (*x,y)
  case [',',_,tuple()]: return (x,*y)
  case [',',*_]: return (x,y)
 raise RuntimeError(f'unrecognized use of ({op}) with args ({x}) and ({y})')

def evl(x:Ast,e=None) -> object:
 e = e or {}
 x = formalize(lamp(x))
 return Eval(e,x)

def Eval(e:dict,x:Ast) -> object:
 if type(x)!=Ast: return x
 if not x.children:
  r = Eval(e,x.node)
  return e[r] if ty(r)==Name else r

 if x.node=='vec':
  t = ty(x.children[0].node)
  return tuple(t(c.node) for c in x.children)

 if x.node in ASSIGN:
  n = x.children[0].node#name
  r = Eval(e,x.children[1])#value
  e[n] = r#FIXME: reference semantics make this update visible to caller; want value semantics
  return r

 if x.node in [*'(;']:#list or sequence
  ks = [Eval(e,i) for i in x.children]
  return ks[-1] if x.node == ';' else ks#progn: last item only

 if x.node in ('{','cmp','prj'): return x#defer eval of lambda, cmp, prj until/if they are applied.

 if x.node in ('@','app'):#"app" always has 2 children  TODO: what about "@"?
  b = Eval(e,x.children[0])#body  (...should it use {**e} instead of e?)
  args = [Eval(e,xi) for xi in x.children[1].children] if x.children[1].node=='[' else [Eval(e,x.children[1])]
  if type(b)==Ast and b.node=='{':
   newenv = {a.node:v for a,v in zip(b.children[0].children,args)}
   return Eval({**e,**newenv},b.children[1])
  raise RuntimeError(f'nyi: {x}')

 if type(x.node)==str and x.node[0] in VERB:
  k = [Eval(e,c) for c in x.children[::(-1,1)[x.node in '(;']]]
  return (0,v1,v2)[len(x.children)](x.node,*k[::-1])
 else:
  raise RuntimeError(f'ast not recognized: {x}')
