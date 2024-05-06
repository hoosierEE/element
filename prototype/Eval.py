from Ast import Ast
from Builtin import COPULA,VERB
from Sema import lift_prj,formalize
class Sym(str):pass
class Name(str):pass
#Vectors; strand/list notation, or construct with ops:
#1 2 3 ⇒ [1, 2, 3]⊂I
#1 2.0 ⇒ [1.0, 2.0]⊂F
#(1.0;2.0) ⇒ [1.0, 2.0]⊂F
#1,2   ⇒ [1, 2]⊂I
#List types
#any type, any shape ("ab";1)⊂L
#1 type, any shape (1;2;3)⊂LI  (0;((1;2);3);4)⊂LI
#tensor (1 type, defined shape): ((1;2;3);(4;5;6))⊂I(2;3)
#Dict types
#generic {a:1;b:("hi";"world")}⊂D
#unitype {a:1;b:(2;3)}⊂DI  {a:1.0;b:(2.0;3.0)}⊂DF
#table {a:(1;2);b:(3;4)}⊂TI
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

def v2(op:str,a,b):
 if type(a)==type(b)==Val:
  return v2val(op,a,b)
 # if type(a)==list and type(b)==Val:
 #  raise 'nyi'
 raise RuntimeError(f'nyi: {op} not defined for {a}{op}{b}')

def Eval(x:Ast|Val) -> Val:
 def _Eval(e,x) -> Val:
  if type(x)==Val: return x
  if type(x)==str: return Val('v',x) if x in VERB else Val(Ty[t:=ty(x)],t(x))
  if type(x)==Ast:
   if not x.children:
    r = _Eval(e,x.node)
    if r.t=='n': return e[r.v]
    return r

   if x.node=='vec':
    t = ty(x.children)
    return Val(Ty[t].upper(),[t(c.node) for c in x.children])

   if x.node in COPULA:
    n = x.children[0].node#name
    r = _Eval(e,x.children[1])#value
    e[n] = r#NOTE: reference semantics make this update visible to caller
    return r

   if x.node in ('cmp','prj','{'): return x
   if x.node=='app':
    x = formalize(lift_prj(x))
    b = _Eval(e,x.children[0])#body hm... should it use {**e} instead of e?
    a = _Eval(e,x.children[1])#args
    if type(b)==Ast and b.node=='{':
     match a:
      case Val(t,v): args = [v]
      case Ast('(',c)|Ast('[',c): args = [_Eval({**e},ci) for ci in c]
      case Ast(_,c): args = [c]
     formal = b.childre[0].children
     for k,v in zip(args,formal):
      if v=='_':
       raise "aaaaah"

     print(b.children[0].children)
     #lambda application (app (lam (prg x) (x)) 5)
     #lambda args: (prg x)
     #lambda body: (x)
     #environment: {'x':5}
     #evaluate lambda body with environment where each (prg x) is replaced by applied argument

    if type(b)==Val:
     if b.t.isupper() and a.t=='a':
      return v2('@',b,a)

    raise RuntimeError(f'nyi: (app {x})')

   if x.node[0] in VERB:
    k = [_Eval(e,c) for c in x.children[::(-1,1)[x.node in '(;']]]
    print('verb',k)
    return (0,v1,v2)[len(x.children)](x.node,*k[::-1])
   else:
    raise RuntimeError(f'ast not recognized: {x}')
  raise RuntimeError('wat?!')
 return _Eval({},x)
