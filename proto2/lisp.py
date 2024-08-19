# lisp.py: λ-calculus with integers, subtraction, variables, conditionals, and closures.
# NOTE: Split and Parse courtesy of https://www.norvig.com/lispy.html
def Split(x:str)->list:
  return x.replace('(',' ( ').replace(')',' ) ').split()

def Parse(x:list)->list:
  t = x.pop(0)
  if t=='(':
    l = []
    while x[0]!=')': l.append(Parse(x))
    x.pop(0)
    return l
  elif t==')':
    raise SyntaxError('unexpected ")"')
  else:
    return int(t) if t.isnumeric() else t

def Eval(e:dict,x:list|int|str)->int|list:#Eval({},Parse(Split('(if 1 42 43)')))
  match x:
    case ('lam',[a,*b],c): return ['lam',a,Eval(e,['lam',b,c])]
    case ('lam',a,b): return x
    case int()|('lam',_,_):return x
    case str():            return e[x]
    case ('-',a,b):        return Eval(e,a)-Eval(e,b)
    case ('let',a,b,c):    return Eval({**e,a:Eval(e,b)},c)
    case ('if',a,b,c):     return Eval(e,b) if Eval(e,a) else Eval(e,c)
    case (('lam',a,b),*c): return Eval({**e,**dict(zip(a,(Eval(e,i) for i in c)))},b) # FIXME: ((lam (a b) b) 1)
    case list():           return Eval(e,[Eval(e,i) for i in x])

if __name__=="__main__":#unit tests
  x = [a.strip() for a in '''
  42 ⇒ 42
  (lam (a b) b) ⇒ ['lam', 'a', ['lam', 'b', 'b']]
  (- 1 4) ⇒ -3
  (let x 1 (- 43 x)) ⇒ 42
  (lam x (- 0 x)) ⇒ ['lam', 'x', ['-', 0, 'x']]
  (if (- 3 3) 1 2) ⇒ 2
  (if 42 1 2) ⇒ 1
  ((lam x x) 3) ⇒ 3
  (let f (lam x 3) (f 1)) ⇒ 3
  (let a 1 ((lam _ a) 2)) ⇒ 1
  (let a 3 (let f (let a 1 (lam _ a)) (f 2))) ⇒ 1
  '''.splitlines()[1:-1]]
  # # failing tests:
  # (let f (let a 1 (lam _ a)) (f 2)) ⇒ 1
  # (if (let x 1 x) x 2) ⇒ 1
  # ((lam (a b) (- a b)) (5 3)) ⇒ 2
  sz = max(map(len,x))
  for t in x:
    i,o = t.split(' ⇒ ')
    try: r = Eval({},Parse(Split(i)))
    except Exception as e: print(f'failing test: {i}','\n',f'exception: {e}'); continue
    print(f'{t:<{sz}}','✅' if str(r)==o else f'❌ got: {r}')
