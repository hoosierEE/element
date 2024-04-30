from Ast import Ast#for type comparison
from Parser import Parse; from Scanner import Scan#imported for repl convenience
class Sym(str):pass
class Name(str):pass
# class Num(float,int):pass
class Val:
 def __init__(s,v):
  if type(v)==Ast:
   if v.node!='vec': raise SyntaxError('not a vector')
   s.vec = 1
   c = [c.node for c in v.children]
   if c0:=c[0][0] in '`"':
    s.t = (str,Sym)[c0=='`']
    s.v = c
   else:
    s.t = (int,float)[any('.' in x for x in c)]
    s.v = list(map(s.t,c))
  else:
   s.vec = 0
   s.t = s.ty(v)
   s.v = s.t(v)
 def __repr__(s):
  t = repr(s.t)[8:-2]
  i = f'[{t}]' if s.vec else t
  return f'{s.v}:{i}'
 def ty(s,x:str):#infer type
  if x[0] in '`"': return (str,Sym)[x[0]=='`']#str
  elif x.isnumeric(): return int
  elif x.count('.')==1 and x.replace('.','').isnumeric(): return float
  elif x[0]=='-' and len(x)>1:
   if x[1:].isnumeric(): return int
   if x.count('.')==1 and x.replace('.','').replace('-','').isnumeric(): return float
   else: return Name
  else: return Name

class VVal(Val):
 def __init__(s,v,t,vec):
  s.v = v
  s.t = t
  s.vec = vec

verb,adverb = '~!@#$%^&*-_=+|:,.<>?',"'/\\"

Num = int|float
ops = {
 ('+',0b00,Num,Num): lambda x,y:x+y,
 ('+',0b01,Num,Num): lambda x,y:[x+yi for yi in y],
 ('+',0b10,Num,Num): lambda x,y:[xi+y for xi in x],
 ('+',0b11,Num,Num): lambda x,y:[xi+yi for xi,yi in zip(x,y)],
 ('-',0b00,Num): lambda y:-y,
 ('-',0b01,Num): lambda y:[-yi for yi in y],
 ('-',0b00,Num,Num): lambda x,y:x-y,
 ('-',0b01,Num,Num): lambda x,y:[x-yi for yi in y],
 ('-',0b10,Num,Num): lambda x,y:[xi-y for xi in x],
 ('-',0b11,Num,Num): lambda x,y:[xi-yi for xi,yi in zip(x,y)],
 ('#',0b00,Num): lambda y:1,
 ('#',0b01,Num): lambda y:len(y),
 ('#',0b00,int,Num): lambda x,y:[y]*x,
 ('#',0b01,int,Num): lambda x,y:y[x:] if x<0 else y[:x],
}

def Ops(op,vec,t1,t2):
 match (op,vec,t1,t2):
  case ['+',0|1|2|3,'int'|'float','int'|'float']: return ops[op,vec,Num,Num]
  case ['-',0|1|2|3,'int'|'float','int'|'float']: return ops[op,vec,Num,Num]
  case ['-',0|1,'int'|'float',None]: return ops[op,vec,Num]
  case ['#',0|1,'int'|'float',None]: return ops[op,vec,Num]
  case ['#',0|1,'int','int'|'float']: return ops[op,vec,int,Num]
  case _: raise Exception('nyi')

def dispatch(v,e,x):
 if len(x)==3:
  if v!='app': raise Exception('dispatch(3) only defined for apply')
  raise Exception('nyi')
 elif len(x)==2:
  R,L = x #fix order (reverse reverse pop)
  tl,tr = (repr(x)[8:-2] for x in (L.t,R.t))
  A = L.vec*2+R.vec
  if A==3 and len(L.v)!=len(R.v): raise Exception('shape mismatch')
  z = Ops(v,A,tl,tr)(L.v,R.v)
  tz = type(z[0]) if type(z)==list else type(z)
  return VVal(z,tz,type(z)==list)
 elif len(x)==1:
  x = x[0]
  t = repr(x.t)[8:-2]
  r = Ops(v,x.vec,t,None)(x.v)
  return VVal(r,x.t,x.vec)
 else:
  raise Exception('no dispatchable 0-argument ops exist')

def Eval(ast:Ast)->list:#depth-first, right-to-left
 def _Eval(s:list,e:dict,ast:Ast):#stack s used for side effects/mutation
  #the basic idea is to first eval ast.children (in the right order)
  #and then finally eval ast.node itself
  #if the node is an operator we apply it immediately to its arguments
  n = ast.node
  if n=='vec':
   s.append(Val(ast))
   return
  ks = ast.children[::(1,-1)[n in ('lst','seq')]]
  for c in ks: _Eval(s,e,c)#evaluate children
  if type(n)==Ast: _Eval(s,e,n)#evaluate node if it's also an AST (i.e: adverb)
  else:
   if n in verb:
    s.append(dispatch(n,e,[s.pop() for _ in range(len(ks))]))
   else:
    s.append(Val(n))

 #hide stack from caller
 e,s = {},[]; _Eval(s,e,ast); return s
