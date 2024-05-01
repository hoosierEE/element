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

def Ops(op,e,x,y):
 if x.v in e: x = e[x.v]
 if y.v in e: y = e[y.v]
 match (op,x.t,y.t):
  case ['+','f'|'i','f'|'i']:return x.v+y.v
  case ['+','f'|'i','F'|'I']:return [x.v+yi for yi in y.v]
  case ['+','F'|'I','f'|'i']:return [xi+y.v for xi in x.v]
  case ['+','F'|'I','F'|'I']:return [xi+yi for xi,yi in zip(x.v,y.v)]
  case ['-','f'|'i',None]:   return -y.v
  case ['-','F'|'I',None]:   return [-a for a in y.v]
  case ['-','f'|'i','f'|'i']:return x.v-y.v
  case ['-','f'|'i','F'|'I']:return [x.v-a for a in y.v]
  case ['-','F'|'I','f'|'i']:return [y.v-a for a in x.v]
  case ['-','F'|'I','F'|'I']:return [a-b for a,b in zip(x.v,y.v)]
  case ['#','i',_]:          return y.v[x.v:] if x.v<0 else y.v[:x.v]
  case [':','n',_]:          e[x.v]=y; return y.v
  case ['#','i',None]:       return 1
  case ['#',_,None]:         return len(y.v)
  case ['!','i',None]:       return list(range(y.v))
  case _: raise Exception('nyi')

def dispatch(v,e,*x):
 if len(x)==3:
  if v!='app': raise Exception('dispatch(3) only defined for apply')
  raise Exception('nyi')
 elif len(x)==2:
  R,L = x #undo reversal due to push/pop
  A = L.t.isupper()*2+R.t.isupper()
  if A==3 and len(L.v)!=len(R.v): raise Exception('shape mismatch')
  z = Ops(v,e,L,R)
  tz = Ty[type(z[0])].upper() if type(z)==list else Ty[type(z)]
  return VVal(z,tz)
 elif len(x)==1:
  z = Ops(v,e,x[0],None)
  tz = Ty[type(z[0])].upper() if type(z)==list else Ty[type(z)]
  return VVal(z,tz)
 else:
  raise Exception('no dispatchable 0-argument ops exist')

def Eval(ast:Ast)->list:
 def _Eval(s:list,e:dict,ast:Ast):#(s)tack and its (e)nvironmental name bindings
  #basic idea (depth first, post-order traversal)
  #1.evaluate ast.children (in the correct order)
  #2.evaluate ast.node
  #operands: push
  #operators: lookup fn, pop #args, apply and push result
  #TODO:
  #iterators: create fn, pop #args, apply and push result
  #assign: check mutability, (insert into/update/read from/delete) environment
  if (n:=ast.node)=='vec': return s.append(Val(ast))
  # elif n=='NIL': return
  ks = ast.children[::(1,-1)[n in ('lst','seq')]]#lst and seq evaluate from left to right
  for c in ks: _Eval(s,e,c)#evaluate children in current env
  if type(n)==Ast: _Eval(s,{**e},n)#copy env
  elif n=='app':
   if ks[0].node in adverb:
    ...
   if n in adverb:
    ...
  else:
   if ks and n in verb:#the easy part
    s.append(dispatch(n,e,*(s.pop() for _ in range(len(ks)))))
   elif n in ('prj','cmp'):
    if len(ks)==2: v,o = [s.pop(),s.pop()]; s.append(v)#dip
    else: o = s.pop()
    s.append(VVal(o.v,n))
   elif n in adverb:#first child of app
    s.append(VVal(n,'adv'))
   else:
    s.append(Val(n))

 #hide stack from caller
 e,s = {},[]
 _Eval(s,e,ast)
 print(e)
 print(s)
 return s.pop()
 # try:
 #  _Eval(s,e,ast)
 #  return s
 # except Exception as e:
 #  print(e)
