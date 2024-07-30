from .Ast import Ast
from .Semantic import Val,Name
import operator as op

type Expr = float|int|list|Name|Nil

def Env() -> dict:
 return {
  '-': op.sub,
  '+': op.add,
  # 'app': lambda x,y: x(*y),
 }

def Eval(x:Expr,e:dict) -> Expr:
 # print(dict(set(e.items()-set(Env().items()))),x)
 match x:
  case Name(): return e[x]
  case Val() if isinstance(x.v,str): return x.t(x.v)
  case Val() if isinstance(x.v,Ast): return [x.t(v.node) for v in x.v.children]
  case float()|int()|('{',_,_): return x
  case Ast(): return Eval([x.node,*x.children],e)
  case (':',a,b):
   k = Eval(a,e) if a.v in e else a.v
   e[k] = Eval(b,e)
   return e[k]
  case ('(',*xs): return [Eval(x,e) for x in xs]
  case (';',*xs): return Eval([Eval(x,e) for x in xs][-1],e)
  case (f,*xs) if f in e: return e[f](*(Eval(a,e) for a in xs))
  case (f,*xs) if f=='app':
   # TODO
   return 0
  case list(): return [Eval(i,e) for i in x]
  case _: print('wat?',x)
