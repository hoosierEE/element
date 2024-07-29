from .Ast import Ast
from .Semantic import Val,Name
import operator as op

type Expr = float|int|list|str

def Env() -> dict:
 return {
  '-': op.sub,
  '+': op.add,
 }

def Eval(x:Expr,e:dict) -> Expr:
 # print(dict(set(e.items()-set(Env().items()))),x)
 match x:
  case Name()|str(): return e[x]
  case Val(): return Eval(x.t(x.v),e)
  case float()|int()|('{',_,_): return x
  case Ast(): return Eval([x.node,*x.children],e)
  case (':',a,b):
   k = Eval(a,e) if a.v in e else a.v
   e[k] = Eval(b,e)
   return e[k]
  case ('(',*xs): return [Eval(x,e) for x in xs]
  case (';',*xs): return Eval([Eval(x,e) for x in xs][-1],e)
  case (op,*xs) if op in e:
   proc = e[op]
   args = [Eval(a,e) for a in xs]
   return proc(*args)
  case list(): return Eval([Eval(i,e) for i in x],e)
