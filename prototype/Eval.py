'''Eval.py - interpret a parsed expression'''
Expr = float|list|str
class Sym(str):pass
class Name(str):pass

def ty1(x:str) -> type:
 if x[0] in '`"': return (str,Sym)[x[0]=='`']
 if x.replace('.','').replace('-','').isnumeric(): return float
 return Name

def infer_lit(x:Expr)->Expr:
 '''infer types for literals'''
 match x:
  case ('vec',*a): t = [ty1(i) for i in a]
  case _: raise TypeError(f'unmatched pattern: {x}')

def ev(x:Expr)->Expr: return Eval({},infer_lit(x))
def Eval(e:dict,x:Expr)->Expr:
 match x:
  case float()|('lam',_,_):return x
  case str():              return e[x]
  case ('-',a,b):          return Eval(e,a)-Eval(e,b) # TODO: all the other operators
  case ('let',a,b,c):      return Eval({**e,a:Eval(e,b)},c)
  case ('if',a,b,c):       return Eval(e,b) if Eval(e,a) else Eval(e,c)
  case (('lam',a,b),*c):   return Eval({**e,**dict(zip(a,(Eval(e,i) for i in c)))},b)
  case list():             return Eval(e,[Eval(e,i) for i in x])
