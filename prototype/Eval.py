from .Ast import Ast
from .Semantic import Val,Name
import operator as op
type Expr = float|int|list|Name|Nil

def Env() -> dict:
 return {
  '-': op.sub,
  '+': op.add,
 }

def Eval(x:Expr,e:dict) -> Expr:
 # print(dict(set(e.items()-set(Env().items()))),x)
 match x:
  case Val() if isinstance(x.v,Ast): return [x.t(v.node) for v in x.v[1]]
  case Val() if x.t == Name: return e[x.v]
  case Val(): return x.t(x.v)
  case Ast(): return Eval([x.node,*x[1]],e)
  case (':',a,b):
   k = Eval(a,e) if a.v in e else a.v
   e[k] = Eval(b,e)
   return e[k]
  case ('(',*xs): return [Eval(x,e) for x in xs]
  case (';',*xs): return Eval([Eval(x,e) for x in xs][-1],e)
  case ('app',a,b):
   (an,ac),(bn,bc) = a.t,b.t
   if an+bn=='{[': # FIXME - handle projection
    args = [x.v for x in ac[0][1]]
    given = [Eval(i,e) for i in bc]
    return Eval(ac[1],{**e,**dict(zip(args,given))})
   return 42
  case (f,*xs) if f in e: return e[f](*(Eval(a,e) for a in xs))
  case list(): return [Eval(i,e) for i in x]
  case _: return x
