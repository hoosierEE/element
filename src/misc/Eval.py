#input: AST
#output: evaluate expressions to produce results, persist variables, side effects
#NOTE
#operator overloading is based on arity as well as type,
#so when we go to evaluate an operator, we actually need a compound key:
# (symbol, *types) where (types) contains the right argument and sometimes
# a left argument too. Additionally some overloads are not just type but also value.
#for example:
# !i ⇒ enum/range
# !I ⇒ odometer
# !d ⇒ keys
# !S ⇒ namespace keys
# -i!I ⇒ integer division
# i!I ⇒ modulo
# x!y ⇒ dict
from Ast import Ast#for type comparison
from Parser import Parse; from Scanner import Scan#imported for repl convenience
class sym(str):pass

# TODO:
# pass: annotate types
# func: choose func based on arity, types, etc.
def ty(x:str):#infer type
 if x[0] in '`"': return (str,sym)[x[0]=='`']
 return float if '.' in x else int

ops = {
 '-': lambda x,y:x-y,
 '-:': lambda x:-x,
 '+': lambda x,y:x+y,
 '*': lambda x,y:x*y,
 '*:': lambda x:x[2],
 '#': lambda x,y:y[:x],#(i#y) "take" is structural, not pervasive
 '#:': lambda x:len(x) if type(x)in(tuple,list) else 1,#also structural
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
  if ast.node=='arr':#infer type for strand literals (any float⇒float)
   cs = [x.node for x in ast.children]
   c0 = cs[0][0]
   if c0 in '"`': cls = (str,sym)[c0=='`']
   else:          cls = (int,float)[any('.' in x for x in cs)]
   s.append(('arr',cls,*cs))
   return
  for c in ast.children[::-1]: _Eval(s,c)
  if type(ast.node)==Ast: _Eval(s,ast.node)
  else:
   x = ast.node+':'*(len(ast.children)==1)
   if x in ops:
    s.append(sa(x,*(s.pop() for _ in range(len(ast.children)))))
   elif x in ('app','cmp','prj'):
    print(x)
   else:
    s.append(ty(x)(x))#scalar literal

 #hide stack from caller
 s = []; _Eval(s,ast); return s
