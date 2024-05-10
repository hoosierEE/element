# TODO: simplify (prototype only)
# get rid of integers
# don't save type info; instead compute it on-demand
# use plain Python values instead of Val class
from Ast import Ast
from Builtin import ASSIGN,VERB
from Semantic import lift_prj,formalize
class Sym(str):pass
class Name(str):pass
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
  #TODO: handle numeric types better, 'min' is brittle
  case ['-','f'|'i','f'|'i']: return Val(min(a.t,b.t),a.v-b.v)
  case ['-','f'|'i','F'|'I']: return Val(min(a.t,b.t).upper(),[a.v-x for x in b.v])
  case ['-','F'|'I','f'|'i']: return Val(min(a.t,b.t).upper(),[x-b.v for x in a.v])
  case ['-','F'|'I','F'|'I']: return Val(min(a.t,b.t).upper(),[x-y for x,y in zip(a.v,b.v)])

  # case [',','f'|'i','f'|'i']: return Val(min(a.t,b.t).upper(),[a.v,b.v])
  # case [',','F'|'I','f'|'i']: return Val(min(a.t,b.t),[*a.v,b.v])
  # case [',','f'|'i','F'|'I']: return Val(min(a.t,b.t),[a.v,*b.v])
  case [',',t,u] if t==u and t.islower(): return Val(t.upper(),[a.v,b.v])
  case [',',t,u] if t==u and t.isupper(): return Val(t,[*a.v,*b.v])
  case [',',t,u] if t.isupper() and u.islower(): return Val('L',[*a.v,b.v])
  case [',',t,u] if t.islower() and u.isupper(): return Val('L',[*a.v,b.v])
  case [',',t,u]: return Val('L',[*a.v,*b.v])

  # case [',',t,u]:
  #  if hasattr(a.v,'__len__') and hasattr(b.v,'__len__'): return Val('L',[*a.v,*b.v])
  #  if hasattr(a.v,'__len__'):                            return Val('L',[*a.v,b.v])
  #  if hasattr(b.v,'__len__'):                            return Val('L',[a.v,*b.v])
  #  return Val(min(t,u),[a.v,b.v])
  case ['@','L','i']: return Val(Ty[type(r:=a.v[b.v])],r)#TODO: outdex
  case ['@',t,'i'] if t.isupper(): return Val(Ty[type(r:=a.v[b.v])],r)#TODO: outdex
  case _: raise RuntimeError(f'nyi: {op} {a} {b}')

def v2(op:str,a,b):
 if type(a)==type(b)==Val: return v2val(op,a,b)
 raise RuntimeError(f'nyi: {op} not defined for {a}{op}{b}')

def evl(x:Ast,e=None) -> Val:
 e = e or {}
 x = formalize(lift_prj(x))
 return Eval(e,x)

def Eval(e,x) -> Val:
 if type(x)==Val: return x
 if type(x)==str: return Val('v',x) if x in VERB else Val(Ty[t:=ty(x)],t(x))
 if type(x)==Ast:
  if not x.children:
   r = Eval(e,x.node)
   if r.t=='n': return e[r.v]
   return r

  if x.node=='vec':
   t = ty(x.children)
   return Val(Ty[t].upper(),[t(c.node) for c in x.children])

  if x.node in ASSIGN:
   n = x.children[0].node#name
   r = Eval(e,x.children[1])#value
   e[n] = r#NOTE: reference semantics make this update visible to caller
   return r

  if x.node in [*'(;']:#list or sequence
   ks = [Eval(e,i) for i in x.children]
   if x.node == ';': return ks[-1]#return the last of the sequence (progn)
   return Val('L',ks)

  if x.node in ('{','cmp','prj'): return x#defer eval of lambda, cmp, prj until/if they are applied.

  if x.node in ('@','app'):#"app" always has 2 children  TODO: what about "@"?
   b = Eval(e,x.children[0])#body  (...should it use {**e} instead of e?)
   args = [Eval(e,xi) for xi in x.children[1].children] if x.children[1].node=='[' else [Eval(e,x.children[1])]
   if type(b)==Ast and b.node=='{':
    newenv = {a.node:v for a,v in zip(b.children[0].children,args)}
    return Eval({**e,**newenv},b.children[1])
   if type(b)==Val:
    #FIXME: "a" not defined
    # a = args[0] # not quite...
    if b.t.isupper() and a.t=='a': return v2('@',b,a)

   raise RuntimeError(f'nyi: {x}')

  if type(x.node)==str and x.node[0] in VERB:
   k = [Eval(e,c) for c in x.children[::(-1,1)[x.node in '(;']]]
   return (0,v1,v2)[len(x.children)](x.node,*k[::-1])
  else:
   raise RuntimeError(f'ast not recognized: {x}')
 raise RuntimeError('wat?!')
