from Ast import Ast#for type comparison
from Parser import Parse; from Scanner import Scan#imported for repl convenience
class Sym(str):pass
class Name(str):pass
Ty = dict(zip((Name,Sym,dict,float,int,list,str),'nsdfilc'))
def ty(x:str):#infer type
 floaty = lambda x:x.count('.')==1 and x.replace('.','') or ''
 if x[0] in '`"': return (str,Sym)[x[0]=='`']#str
 elif x.isnumeric(): return int
 elif floaty(x).isnumeric(): return float
 elif x[0]=='-' and len(x)>1:
  if x[1:].isnumeric(): return int
  if floaty(x).replace('-','').isnumeric(): return float
  else: return Name
 else: return Name

class Val:
 def __init__(s,v):
  if type(v)==Ast:
   if v.node!='vec': raise SyntaxError('not a vector')
   c = [c.node for c in v.children]
   if c0:=c[0][0] in '`"':
    s.t = Ty[(str,Sym)[c0=='`']].upper()
    s.v = c
   else:
    t = (int,float)[any('.' in x for x in c)]
    s.v = list(map(t,c))
    s.t = Ty[t].upper()
  else:
   s.t = Ty[ty(v)]
   s.v = ty(v)(v)
 def __repr__(s):
  return f'{s.v}:{s.t}'

class VVal(Val):
 def __init__(s,v,t):
  s.v = v
  s.t = t

verb,adverb = '~!@#$%^&*-_=+|:,.<>?',"'/\\"

def Ops(op,t1,t2):
 match (op,t1,t2):
  case ['+','f'|'i','f'|'i']:return lambda x,y:x+y
  case ['+','f'|'i','F'|'I']:return lambda x,y:[x+yi for yi in y]
  case ['+','F'|'I','f'|'i']:return lambda x,y:[xi+y for xi in x]
  case ['+','F'|'I','F'|'I']:return lambda x,y:[xi+yi for xi,yi in zip(x,y)]
  case ['-','f'|'i']:        return lambda y:-y
  case ['-','F'|'I']:        return lambda y:[-a for a in y]
  case ['-','f'|'i','f'|'i']:return lambda x,y:x-y
  case ['-','f'|'i','F'|'I']:return lambda x,y:[x-a for a in y]
  case ['-','F'|'I','f'|'i']:return lambda x,y:[y-a for a in x]
  case ['-','F'|'I','F'|'I']:return lambda x,y:[a-b for a,b in zip(x,y)]
  case ['#','i',_]:          return lambda x,y:y[x:] if x<0 else y[:x]
  case ['#','i',None]:       return lambda y:1
  case ['#',_,None]:         return lambda y:len(y)
  case ['!','i',None]:       return lambda y:list(range(y))
  case _: raise Exception('nyi')

def dispatch(v,e,*x):
 if len(x)==3:
  if v!='app': raise Exception('dispatch(3) only defined for apply')
  raise Exception('nyi')
 elif len(x)==2:
  R,L = x #undo reversal due to push/pop
  A = L.t.isupper()*2+R.t.isupper()
  if A==3 and len(L.v)!=len(R.v): raise Exception('shape mismatch')
  z = Ops(v,L.t,R.t)(L.v,R.v)
  tz = Ty[type(z[0])].upper() if type(z)==list else Ty[type(z)]
  return VVal(z,tz)
 elif len(x)==1:
  z = Ops(v,x[0].t,None)(x[0].v)
  tz = Ty[type(z[0])].upper() if type(z)==list else Ty[type(z)]
  return VVal(z,tz)
 else:
  raise Exception('no dispatchable 0-argument ops exist')

def Eval(ast:Ast)->list:
 def _Eval(s:list,e:dict,ast:Ast):#(s)tack (e)nvironment
  #basic idea (depth first, post-order traversal)
  #1.evaluate ast.children (in the correct order)
  #2.evaluate ast.node
  #operands: push
  #operators: lookup fn, pop #args, apply and push result
  #TODO:
  #iterators: create fn, pop #args, apply and push result
  #assigns: check mutability, (insert into/update/read from/delete) environment
  n = ast.node
  if n=='vec': return s.append(Val(ast))
  ks = ast.children[::(1,-1)[n in ('lst','seq')]]#lst and seq evaluate from left to right
  for c in ks: _Eval(s,e,c)#evaluate children
  if type(n)==Ast: _Eval(s,e,n)#evaluate node if it's also an AST (adverb,lambda,projection,...)
  else:
   if ks and n in verb: s.append(dispatch(n,e,*(s.pop() for _ in range(len(ks)))))#the easy part
   elif n=='app':
    print(n,ks)
    # x = [s.pop() for _ in range(len(ks))][::-1]
    # print(n,x)
    ... #TODO
   elif n in adverb:
    print('adverb',n,ks)
    x = [s.pop() for _ in range(len(ks))][::-1]
    ... #TODO
   else:
    s.append(Val(n))

 #hide stack from caller
 e,s = {},[]; _Eval(s,e,ast); return s
