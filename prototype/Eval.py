# BETTER IDEA:
# rather than DFS to construct an RPN representation,
# just eval directly with recursive descent..
from Ast import Ast
from Builtin import COPULA,VERB
class Sym(str):pass
class Name(str):pass
#Vectors
#1 2 3 ⇒ (1 2 3):I
#1 2.0 ⇒ (1.0 2.0):F
#List subtypes
#1.any type/shape ("ab";1)
#2.1 type, any shape (1;2;3):I.3 or (0;((1;2);3);4):(I)
#3.tensor ((1;2;3);(4;5;6)):I.2.3
#Dict subtypes
#1.generic {a:1;b:("hi";"world")}:D≠
#2.unitype {a:1;b:(2;3)}:DI
#3.table {a:(1;2);b:(3;4)}:T
Ty = dict(zip((str,Sym,Name,int,float,dict,list),'csnifDL'))
Yt = {b:a for a,b in Ty.items()}
class Val:
 def __init__(s,t,v): s.t,s.v = t,v
 def __repr__(s): return f'{s.v}:{s.t}'

def isnumeric(x:str) -> bool:
 return x.replace('.','').replace('-','').isnumeric()

def ty(x:str|tuple|list) -> type:
 if type(x) in (list,tuple):
  c00 = x[0].node[0]
  if c00 in '"`': t = (str,Sym)[c00=='`']
  else: t = float if any('.' in c.node for c in x) else int
  return t
 if type(x)==str:
  if x[0] in '"`': return (str,Sym)[x[0]=='`']
  if isnumeric(x): return float if '.' in x else int
  return Name
 return type(x)

def v1(op:str,val:Val):
 match (op,val.t):
  case ['-','f'|'i']: return Val(val.t,-val.v)
  case ['-','F'|'I']: return Val(val.t,[-x for x in val.v])
  case [',',t] if t.islower(): return Val(t.upper(),[val.v])
  case [',',t]: return Val('L',[val.v])
  case ['@',t]: return t
  case _: raise RuntimeError('nyi')

def v2val(op:str,a:Val,b:Val) -> Val:
 match (op,a.t,b.t):
  case ['-','f'|'i','f'|'i']: return Val(min(a.t,b.t),a.v-b.v)
  case ['-','f'|'i','F'|'I']: return Val(min(a.t,b.t).upper(),[a.v-x for x in b.v])
  case ['-','F'|'I','f'|'i']: return Val(min(a.t,b.t).upper(),[x-b.v for x in a.v])
  case ['-','F'|'I','F'|'I']: return Val(min(a.t,b.t).upper(),[x-y for x,y in zip(a.v,b.v)])
  case [',','f'|'i','f'|'i']: return Val(min(a.t,b.t).upper(),[a.v,b.v])
  case [',','F'|'I','f'|'i']: return Val(min(a.t,b.t).upper(),[*a.v,b.v])
  case [',','f'|'i','F'|'I']: return Val(min(a.t,b.t).upper(),[a.v,*b.v])
  case ['@','L','i']: return Val(Ty[type(r:=a.v[b.v])],r)#TODO: outdex
  case ['@',t,'i'] if t.isupper(): return Val(Ty[type(r:=a.v[b.v])],r)#TODO: outdex
  case _: raise RuntimeError('nyi')

# def v2(op:str,a,b):
#  if type(a)==type(b)==Val: return v2val(op,a,b)
#  if type(a)==list and type(b)==Val:

def Eval(x) -> Val:
 def _Eval(x,e) -> Val:
  if type(x)==Val: return x
  if type(x)==str: return Val('v',x) if x in VERB else Val(Ty[t:=ty(x)],t(x))
  if type(x)==Ast:
   if not x.children:
    r = _Eval(x.node,e)
    if r.t=='n': return e[r.v]
    return r

   if x.node=='vec':
    t = ty(x.children)
    return Val(Ty[t].upper(),[t(c.node) for c in x.children])

   if x.node in COPULA:
    n = x.children[0].node#name
    r = _Eval(x.children[1],e)#value
    e[n] = r
    return r

   if x.node in ('cmp','prj'): return x

   if x.node=='app':
    r = _Eval(x.children[0],e)
    i = _Eval(x.children[1],e)

    #TODO: what if r has no .t?
    if r.t.isupper() and i.t=='i':
     return v2('@',r,i)

    print('app',x)
    raise RuntimeError('nyi')

   if x.node[0] in VERB:
    k = [_Eval(c,e) for c in x.children[::(-1,1)[x.node in '(;']]]
    return (0,v1,v2)[len(x.children)](x.node,*k[::-1])
   else:
    raise RuntimeError(f'ast not recognized: {x}')
  raise RuntimeError('wat?!')
 return _Eval(x,{})
