from .Ast import Ast
from .Builtin import ASSIGN,VERB
from dataclasses import dataclass

type Builtin = str
type Name = str
type Nil = None
type Sym = str

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
  return f'{s.v}:{st}'

def vectype(xs:list[Ast]) -> type:
 types = {ty(x.node) for x in xs}
 return float if int in types and float in types else types.pop()

def infer(a:Ast) -> Val:
 '''infer types from literal expressions'''
 match (a.node,a.children):
  case ('vec',b): return Val(a,vectype(b))
  case ('{',p,b): return Ast(a.node,*map(infer,a.children))
  case ('[',()): return Val(a.node,'NIL')
  case (node,()): return Val(node,ty(node[0]))
  case (node,children): return Ast(a.node,*map(infer,children))
  case _: raise SyntaxError(f'unmatched: {a}')

def lamp(a:Ast) -> Ast:
 '''convert projection to lambda'''
 ax,ay = Ast('x'),Ast('y')
 match a.node,len(a.children):
  case 'prj',1:
   if (v:=a.children[0].node)[0] in VERB and v.endswith(':'):
    return Ast('{',Ast('[',ax), Ast(v,ax))
   return Ast('{',Ast('[',ax,ay), Ast(v,ax,ay))
  case 'prj',2:
   return Ast('{',Ast('[',ax), Ast(a.children[0].node,lamp(a.children[1]),ax))
 return Ast(a.node, *map(lamp,a.children))

def lamc(a:Ast) -> Ast:
 '''merge compositions into inner lambda'''
 # print(a)
 if a.node == 'cmp':
  if a.children[1].node == '{' and a.children[0].node != '{':
   x = Ast('{', a.children[1].children[0], Ast(a.children[0].node, a.children[1].children[1]))
   print('first',x)
   return x
  elif a.children[1].node == 'cmp':
   print('..',a.children[1])
   x = lamc(Ast('cmp', a.children[0], lamc(a.children[1])))
   print(x)
   return x
  else:
   return 42
   return Ast(a.node, *(lamc(x) for x in a.children))
   # return a
 else:
  return 43
  return Ast(a.node, *(lamc(x) for x in a.children))



 # match a.node:
 #  case 'cmp':
 #   # print(a.children[0].node, a.children[1].node)
 #   match (a.children[0].node, a.children[1].node):
 #    # case ('{','{'): return Ast('app',*(lamc(x) for x in a.children))
 #    case (b,'{'): print('leaf'); _,(c,d) = a.children[1]; return Ast('{',c,lamc(Ast(b,d)))
 #    # case (b,'cmp'): print('recur'); return Ast(b, *a.children[1].children)
 #    case _: return a
 #    # case b,c: return Ast(a.node, *(lamc(x) for x in a.children[1].children))
 #  case _: return Ast(a.node, *(lamc(x) for x in a.children))

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
 '''semantic analysis wrapper'''
 return infer(formalize(lamp(a)))
