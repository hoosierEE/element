from .Parser import Ast,NIL
from .Builtin import ASSIGN,VERB
from dataclasses import dataclass
class LengthError(Exception): pass
class Builtin(str): pass
class Name(str): pass
class Nil(object): pass
class Sym(str): pass

def ty(x:str) -> type:
 '''infer types of literals'''
 if x[0] in '`"': return (str,Sym)[x[0]=='`']
 if x.replace('.','').replace('-','').isnumeric(): return float if '.' in x else int
 if x[0] in ASSIGN+VERB: return Builtin
 if x=='NIL': return Nil
 return Name

@dataclass
class Val:
 v:Ast
 t:type
 def __repr__(s):
  r = repr(s.t)
  st = r[8:-2] if '<' in r else r
  st = st.split('.')[-1] # discard "package.module." prefix
  return f'{s.v}:{st}'

def vectype(xs:list[Ast]) -> type:
 types = {ty(x.n) for x in xs}
 return float if (int in types and float in types) else types.pop()

def infer(a:Ast) -> Val:
 '''infer types from literal expressions'''
 match a:
  case str()|None: return a
  case ('vec',b): return Val(a,vectype(b))
  case ('{',b,c): return Ast(a.n,tuple(map(infer,a.c)))
  case ('[',()): return Val(a.n,Nil)
  case (node,()): return Val(node,ty(node))
  case (node,None): return Val(node,ty(node))
  case (node,children): return Ast(a.n,tuple(map(infer,children)))
  case _: raise SyntaxError(f'unmatched: {a}')

def lamp(a:Ast) -> Ast:
 '''convert projection to lambda'''
 px,py = Ast('x'),Ast('y')
 match a:
  case str()|None: return a
  case 'prj',(x,None): return Ast('{',(Ast('[',(px,py)),Ast(x,(px,py))))
  case 'prj',(x,y): return Ast('{',(Ast('[',px),Ast(x.n,(y,px))))
  case _: return Ast(lamp(a.n),tuple(map(lamp,a.c))) if a.c else Ast(a.n)

def lamc(a:Ast) -> Ast:
 '''merge compositions into inner lambda'''
 match a.n:
  case 'cmp': # exactly 2 children
   match a.c[0].n, a.c[1].n:
    case '{','{':
     b1 = a.c[0].c[1]
     args,b2 = a.c[1].c
     return Ast('{',args,Ast(b1.n,b1.c[0],b2))
    case b,'{':
     args,b2 = a.c[1].c
     return Ast('{',args,Ast(a.c[0].n,b2))
    case '{',b: return lamc(Ast('cmp',a.c[0],(lamc(a.c[1]))))
    case b,c: return lamc(Ast('cmp',*map(lamc,a.c))) #lamc(a.c[0]),lamc(a.c[1])))
  case _: return Ast(a.n,tuple(map(lamc,a.c))) if a.c else Ast(a.n)

def get_params(a:Ast) -> str:
 '''get x y z arguments from lambdas'''
 match a:
  case ('x'|'y'|'z',None): return a.n
  case (':'|'::',(b,c)) if b.n in ('x','y','z'): return get_params(c)
  case (_,b): return ''.join(map(get_params,b)) if b else ''

def formalize(a:Ast) -> Ast:
 '''add formal arguments to lambdas'''
 # (λ body) ⇒ args = get_params(body); return (λ (args) formalize(body))
 # (λ ([ args...) body) ⇒ recurse on body
 match a:
  case ('{',(body,)): return Ast('{',(Ast('[',get_params(body)), formalize(body)))
  case ('{',(('[',args),body)): return Ast('{',(Ast('[',args), formalize(body)))
  case b,c: return Ast(formalize(b),formalize(c))
  case _: return a

def Sema(a:Ast) -> Ast|Val:
 '''wrapper function for all the semantic analysis passes, in the right order'''
 return infer(formalize(lamc(lamp(a))))
 # return formalize(lamc(lamp(a)))
