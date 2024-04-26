#input: AST
#output: evaluate expressions to produce results, persist variables, side effects
from Ast import Ast
from Parser import Parse
from Scanner import Scan
# def p(*a,**k): print(*a,**k,end=' ')
def p(x): return str(x)
def ty(x):#get type of literal value
 if x[0] not in '`"':
  if '.' in x: return float
  return int
 return str

ops = {
 '-': lambda x,y:x-y,
 '-:': lambda x:-x,
 '+': lambda x,y:x+y,
 '*': lambda x,y:x*y,
 '*:': lambda x:x[2],
 '#': lambda x,y:x*y,
 '#:': lambda x:len(x),
 '%': lambda x,y:x/y,
 '@': lambda x,y:x[y+2],
 '!:': lambda x:('arr','int',*range(x)),
}

def sa(op,*args):#scalar/array dispatcher
 primary = args[0]
 secondary = args[1] if len(args)>1 else ''
 if secondary:
  if type(primary)==tuple:
   if type(secondary)==tuple:#vec+vec
    assert len(primary) == len(secondary)
    assert primary[1]==secondary[1]#same type
    return (*primary[:2],*(ops[op](x,y) for x,y in zip(primary[2:],secondary[2:])))
   else:#vec+atom
    return (*primary[:2],*(ops[op](x,secondary) for x in primary[2:]))
  elif type(secondary)==tuple:#atom+vec
   return (*secondary[:2],*(ops[op](primary,y) for y in secondary[2:]))
  else:
   return ops[op](primary,secondary)
 else:
  if type(primary)==tuple:
   return (*primary[:2],*(ops[op](p) for p in primary[2:]))
  return ops[op](primary)

def Eval(ast:Ast)->list:#depth-first, right-to-left
 def _Eval(s:list,ast):#stack s used for side effects/mutation
  if ast.node=='arr':
   cs = [x.node for x in ast.children]
   c0 = cs[0][0]
   if c0 in '"`':
    cls = {'"':'str','`':'sym'}[c0]
   else:
    cls = ('int','flt')[any('.' in x for x in cs)]
    cs = map(int if cls=='int' else float,cs)
   s.append(('arr',cls,*cs))

  else:
   for c in ast.children[::-1]:
    _Eval(s,c)
   if type(ast.node)==Ast:
    _Eval(s,ast.node)
   else:#operators, etc.
    x = ast.node+':'*(len(ast.children)==1)
    if x in ops:
     k = [s.pop() for _ in range(len(ast.children))]
     s.append(sa(x,*k))
    else:#scalars
     s.append(ty(x)(x))

 #hide stack from caller
 s = []; _Eval(s,ast); return s
