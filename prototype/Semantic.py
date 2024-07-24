from .Ast import Ast
from .Builtin import ASSIGN,VERB
from dataclasses import dataclass

type Sym = str
type Name = str
type Builtin = str

def ty(x:str) -> type:
 if x[0] in '`"': return (str,Sym)[x[0]=='`']
 if x.replace('.','').replace('-','').isnumeric(): return float if '.' in x else int
 if x=='NIL': return type(None)
 if x[0] in ASSIGN+VERB: return Builtin
 return Name

@dataclass
class Val:
 v:Ast
 t:type
 def __repr__(s):
  r = repr(s.t)
  st = r[8:-2] if '<' in r else r
  return f'{s.v}:{st}'

def infer(a:Ast) -> Val:
 '''infer types from literal expressions'''
 match (a.node,a.children):
  case ('vec',b): return Val(a,ty(b[0].node))
  case ('{',p,b): return Ast(a.node,*map(infer,a.children))
  case ('[',()): return Val(a.node,'NIL')
  case (node,()): return Val(node,ty(node[0]))
  case (node,children): return Ast(a.node,*map(infer,children))
  case _: raise SyntaxError(f'unmatched: {a}')

def lam_from_prj(a:Ast) -> Ast:
 '''convert projection to lambda'''
 ax,ay = Ast('x'),Ast('y')
 match a.node,len(a.children):
  case 'prj',1:
   if (v:=a.children[0].node)[0] in VERB and v.endswith(':'):
    return Ast('{',Ast('[',ax), Ast(v,ax))
   return Ast('{',Ast('[',ax,ay), Ast(v,ax,ay))
  case 'prj',2:
   return Ast('{',Ast('[',ax), Ast(a.children[0].node,lam_from_prj(a.children[1]),ax))
 return Ast(a.node, *map(lam_from_prj,a.children))

def get_params(a:Ast) -> str:
 '''get x y z arguments from lambdas'''
 if a.node=='{': return ''
 if a.node in ASSIGN and a.children[0].node in 'xyz': return ''
 if a.node in [*'xyz']: return a.node
 return ''.join(sorted(get_params(x) for x in a.children))

def formalize(a:Ast) -> Ast:
 '''add formal arguments to lambdas'''
 if a.node=='{' and len(a.children)==1:#lambda without arg list
  if xyz := get_params(a.children[0]):#insert placeholders: xz ⇒ x_z
   xyz = ''.join(x if x in xyz else '_' for x,_ in zip('xyz',range(ord(max(xyz))-ord('w'))))
  return Ast(a.node, Ast('[',*(map(Ast,filter(str,xyz)))), *map(formalize,a.children))#insert (prg x y z)
 return Ast(a.node, *map(formalize,a.children))

def Sema(a:Ast) -> Ast|Val:
 return infer(formalize(lam_from_prj(a)))
