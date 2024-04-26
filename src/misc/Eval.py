#input: AST
#output: evaluate expressions to produce results, persist variables, side effects
from Ast import Ast
from Parser import Parse
from Scanner import Scan
# def p(*a,**k): print(*a,**k,end=' ')
def p(x): return str(x)
def Eval(ast):#recur depth-first, right-to-left
 t = ''
 if ast.node=='arr':
  cs = [x.node for x in ast.children]
  c0 = cs[0][0]
  if c0 in '"`':
   cls = {'"':'str','`':'sym'}[c0]
  else:
   cls = ('int','flt')[any('.' in x for x in cs)]
   cs = map(int if cls=='int' else float,cs)
  t += ' '+p((cls,*cs))
 else:
  for c in ast.children[::-1]:
   t += Eval(c)
  if type(ast.node)==Ast:
   t += Eval(ast.node)
  else:
   t += ' '+p(ast.node+':'*(len(ast.children)==1))
 return t
