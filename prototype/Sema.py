'''
These transformations should happen before Eval.
e.g: formalize(lift_prj(Parse(Scan("x+1"))))

        Parse                     formalize
{1+x-3}   ⇒   (lam (+ 1 (- x 3)))     ⇒     (lam (prg x) (+ 1 (- x 3)))
{x-y}     ⇒   (lam (+ x y))           ⇒     (lam (prg x y) (+ x y))
{3}       ⇒   (lam 3)                 ⇒     (lam prg 3)

   Parse           lift_prj
3-   ⇒   (prj - 3)    ⇒     (lam (prg x) (- 3 x))
-    ⇒   (prj -)      ⇒     (lam (prg x y) (- x y))
'''
from Ast import Ast
from Builtin import COPULA,VERB

def lift_prj(a:Ast) -> Ast:
 '''projection ⇒ lambda'''
 match a.node,len(a.children):
  case 'prj',1:
   if (v:=a.children[0].node)[0] in VERB and v.endswith(':'):
    return Ast('{',Ast('[',Ast('x')), Ast(a.children[0],Ast('x')))
   return Ast('{',Ast('[',*map(Ast,'xy')), Ast(a.children[0],*map(Ast,'xy')))
  case 'prj',2:
   return Ast('{',Ast('[',Ast('x')), Ast(a.children[0],Ast('x'),lift_prj(a.children[1])))
 return Ast(a.node, *map(lift_prj,a.children))

def get_params(a:Ast) -> str:
 '''get x y z arguments from lambdas'''
 if a.node=='{': return ''
 if a.node in COPULA and a.children[0].node in 'xyz': return ''
 if a.node in [*'xyz']: return a.node
 return ''.join(sorted(get_params(x) for x in a.children))

def formalize(a:Ast) -> Ast:
 '''add formal arguments to lambdas'''
 if a.node=='{' and len(a.children)==1:#lambda without arg list
  if xyz := get_params(a.children[0]):#insert placeholders: xz ⇒ x_z
   xyz = ''.join(x if x in xyz else '_' for x,_ in zip('xyz',range(ord(max(xyz))-ord('w'))))
  return Ast(a.node, Ast('[',*(map(Ast,filter(str,xyz)))), *map(formalize,a.children))#insert (prg x y z)
 return Ast(a.node, *map(formalize,a.children))
