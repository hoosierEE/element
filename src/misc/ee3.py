from Ast import Ast
S,Z = str.split,lambda x,y:dict(zip(x,y))
NIL,OP,CP = Ast('NIL'),'({[',')}]'
P,V,A,Q = 0,1,2,3#precedence levels
ac = S("   '   /   \\")#adverb char
an = S('  ech red scn')#adverb name
ap = Z(an,(A,  A,  A,))#{adverb:precedence}
bc = S('   [   *   +   -   ; ')#binary char
bn = S('  fun mul add sub seq')#binary name
bp = Z(bn,(P,  V,  V,  V,  Q,))#{binary:precedence}
uc = S('   [   (   {    #    - ')#UNARY char
un = S('  PRG LST LAM COUNT NEG')#UNARY name
up = Z(un,(P,  P,  P,   V,   V,))#{UNARY:precedence}
ab,bt,ut = Z(ac,an),Z(bc,bn),Z(uc,un)
ps = {**bp,**up,**ap,'app':V,'ARG':P}
def parse(text,verbose=0):
 if not text: return
 t,z,s,d = list(text),len(text),[],[]
 def debug(*args,**kwargs):
  if not verbose: return
  ss,sd = ' '.join(s),' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<25}]',*args,**kwargs)

 def r1(op,m='r1'):#reduce top of stack
  if not s: return
  for _ in range((arity:=1+op.islower())-len(d)): d.append(NIL)
  x,k = s.pop(),[d.pop() for _ in range(arity)][::-1]
  debug(f'{m}:({x=},{k=})')
  if   x=='LST': x,*k = (x,*k[0].children,) if k[0].node=='seq' else k
  elif x in S('ARG PRG') and k[0].node=='seq': k = k[0].children
  elif x=='fun': x,k = k[0],(k[1].children if k[1].node=='seq' else [k[1]])
  elif x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  d.append(Ast(x,*k))

 def reduce_paren():#reduce everything up to open paren, push AST
  while s and (op:=s[-1]) in ps and ps[op]: r1(op,'rp')
  r1(op,'rp')

 def reduce(p):#reduce with prec<p (except paren)
  while s and 0<ps[op:=s[-1]]<p: r1(op,'r')

 def balance(op,bal):
  if op in OP: return bal.append(CP[OP.index(op)])
  if op in CP and (not bal or op!=bal.pop()): raise SyntaxError('unbalanced paren')

 def loop(t,bal,i=0):#advance token, update state
  while True:
   while True:#unary
    if i>=z: return #d.append(NIL)
    c = t[i]
    balance(c,bal)
    debug(c,'→')
    i += 1
    if c==';':
     d.append(NIL)
     s.append(bt[c])
    elif s and s[-1]=='LAM' and c=='[':
     s[-1] = 'lam'
     s.append('ARG')
    elif c in CP:
     # d.append(NIL)
     reduce_paren()
     if not (d and s and d[-1].node=='ARG' and s[-1]=='lam'): break
    elif c in ac:
     s.append(ab[c])
    elif c.isalnum():
     d.append(Ast(c))
     break
    elif c in bt and (i>=z or t[i]in';'+CP):
     s.append(bt[c])
     break
    elif c in ut:
     s.append(ut[c])
    elif c in bt:
     s.append(bt[c])
    else: raise SyntaxError(f'unrecognized unary operator: "{c}"')

   while True:#binary
    if i>=z: return
    c = t[i]
    balance(c,bal)
    debug(c,'↔')
    i += 1
    if c in CP:
     reduce_paren()
     if not (d and s and d[-1].node=='ARG' and s[-1]=='lam'):
      continue
    elif c in bt:
     reduce(ps[bt[c]])
     s.append(bt[c])
     if i<z and t[i] in ';':
      d.append(NIL)
      continue
    elif c in OP:
     s.append('app')
     s.append(ut[c])
    elif c in ac:
     s.append(ab[c])
     continue
    elif c.isalnum():
     s.append('app')
     d.append(Ast(c))
     # continue
    else: raise SyntaxError(f'unrecognized binary operator: "{c}"')
    break

 bal = []
 loop(t,bal)
 debug('done')
 reduce(max(ps.values())+1)
 if len(bal): raise SyntaxError('unbalanaced paren')
 if len(d)!=1: raise SyntaxError(f'data stack: {d}')
 return d.pop()

def test():
 for p in ['']+S('1 x -x 2-x a*b+-c +/x 2+/x -/x #/x +//x (2+)/x'):
  try: parse(p)
  except SyntaxError as e: return print(p,'\t⇒ SyntaxError:',e)
 for b in [' ','(','}','{x}#a']:
  try: parse(b)
  except SyntaxError as e: continue
  return print(repr(b),'\t⇒ should error')
