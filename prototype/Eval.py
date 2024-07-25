type Expr = float|int|list|str

def ev(x:Expr)->Expr:
 return Eval({},x)

def Eval(e:dict,x:Expr)->Expr:
 match x:
  case float()|int()|('lam',_,_): return x
  case str():                     return e[x]
  case ('-',a,b):                 return Eval(e,a)-Eval(e,b) # TODO: all the other operators
  case ('let',a,b,c):             return Eval({**e,a:Eval(e,b)},c)
  case ('if',a,b,c):              return Eval(e,b) if Eval(e,a) else Eval(e,c)
  case (('lam',a,b),*c):          return Eval({**e,**dict(zip(a,(Eval(e,i) for i in c)))},b)
  case list():                    return Eval(e,[Eval(e,i) for i in x])
