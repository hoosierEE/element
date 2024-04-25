#input: AST
#output: evaluate expressions to produce results, persist variables, side effects
from Ast import Ast
from Parser import Parse
from Scanner import Scan
def Eval(ast):#recur depth-first, right-to-left
 if ast.node=='arr':
  print(ast.children)
 else:
  for c in ast.children[::-1]:
   Eval(c)
  if type(ast.node)==Ast:
   Eval(ast.node)
  else:
   print(ast.node)
 print(len(ast.children))
