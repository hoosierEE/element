from .Ast import Ast
from .Builtin import ASSIGN,VERB
from dataclasses import dataclass

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
  return f'{s.v}:{st}'

def vectype(xs:list[Ast]) -> type:
 types = {ty(x.node) for x in xs}
 return float if (int in types and float in types) else types.pop()

def infer(a:Ast) -> Val:
 '''infer types from literal expressions'''
 match (a.node,a.children):
  case ('vec',b): return Val(a,vectype(b))
  case ('{',_): return Ast(a.node,*map(infer,a.children))
  case ('[',()): return Val(a.node,Nil)
  case (node,()): return Val(node,ty(node))
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
  case 'prj',2: return Ast('{',Ast('[',ax), Ast(a.children[0].node,lamp(a.children[1]),ax))
  case _: return Ast(a.node, *map(lamp,a.children))

def lamc(a:Ast) -> Ast:
 '''merge compositions into inner lambda'''
 match a.node:
  case 'cmp': # exactly 2 children
   match a.children[0].node, a.children[1].node:
    case '{','{':
     b1 = a.children[0].children[1]
     args,b2 = a.children[1].children
     return Ast('{',args,Ast(b1.node,b1.children[0],b2))
    case b,'{':
     args,b2 = a.children[1].children
     return Ast('{',args,Ast(a.children[0].node,b2))
    case '{',b: return lamc(Ast('cmp',a.children[0],(lamc(a.children[1]))))
    case b,c: return lamc(Ast('cmp',*map(lamc,a.children))) #lamc(a.children[0]),lamc(a.children[1])))
  case _: return Ast(a.node,*map(lamc,a.children))

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

def par(a:Ast) -> Ast:
 '''
 convert partial applications to new lambdas with fewer args
 (after formalize)
 {x,y}[;2] ⇒ {x,2}
 {x,y,z}[;2] ⇒ {x,2,y}
 {x,y,z}[;;3] ⇒ {x,y,3}
 {z}[3] ⇒ {y}
 {y}[2] ⇒ {x}
 {z}[;4] ⇒ {x}
 {z}[;;2] ⇒ 2
 '''
 match a.node:
  case 'app' if a.children[0].node=='{':
   return ... #TODO
 return Ast(a.node, *map(par,a.children))

def Sema(a:Ast) -> Ast|Val:
 '''wrapper function for all the semantic analysis passes, in the right order'''
 # return infer(formalize(lamc(lamp(a))))
 return (formalize(lamc(lamp(a))))