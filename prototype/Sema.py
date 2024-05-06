'''
semantic analysis and transformations before eval:

        Parse                 formalize:
{1+x-3} ⇒ (lam (+ 1 (- x 3))) ⇒ (lam (prg x) (+ 1 (- x 3)))
{x-y}   ⇒ (lam (+ x y))       ⇒ (lam (prg x y) (+ x y))
{3}     ⇒ (lam 3)             ⇒ (lam prg 3)

    Parse       tolambda:
 3- ⇒ (prj - 3) ⇒ (lam (prg x) (- 3 x))
 -  ⇒ (prj -)   ⇒ (lam (prg x y) (- x y))
'''
from Ast import Ast
from Builtin import COPULA

def get_params(a:Ast) -> str:
 '''get x y z arguments from lambdas'''
 if a.node=='{': return ''
 if a.node in COPULA and a.children[0].node in 'xyz': return ''
 if a.node in [*'xyz']: return a.node
 return ''.join(sorted(filter(str,(get_params(x) for x in a.children))))

def formalize(a:Ast) -> Ast:
 '''add formal arguments to lambdas'''
 if a.node=='{' and len(a.children)==1 and a.children[0]!='[':#lambda without arg list
  formal = get_params(a.children[0])
  return Ast(a.node, Ast('[',*(map(Ast,filter(str,formal)))), formalize(a.children[0]))#insert (prg x y z)
 return Ast(a.node, *map(formalize,a.children)) if a.children else a

def tolambda(a:Ast) -> Ast:
 '''projection ⇒ lambda'''
 match a.node,len(a.children):
  case 'prj',2: return Ast('{',Ast('[',Ast('x')),Ast(a.children[0],Ast('x'),a.children[1]))
  case 'prj',1: return Ast('{',Ast('[',*map(Ast,'xy')),Ast(a.children[0],*map(Ast,'xy')))
 return Ast(a.node, *map(tolambda,a.children))#NOTE:this branch handles the literal "prj" and everything else
