from Ast import Ast
S,Z,NIL = str.split,lambda x,y:dict(zip(x,y)),Ast('nil')
bc = S('   (   *   +   -   ; ')#token
bn = S('  fun mul add sub seq')#name
bp = Z(bn,(0,  1,  1,  1,  2,))#{binary:precedence}
uc = S('   (    #    -   ; ')#token
un = S('  lst count neg nil')#name
up = Z(un,(0,   1,   1,  1,))#{unary:precedence}
bt,ut,ps = Z(bc,bn),Z(uc,un),{**bp,**up,'app':1}#{t:n},{t:n},{n:precedence}
class ParseError(SyntaxError): pass
def parse(text,verbose=0):
 if not text: return Ast(text)
 t,z,s,d = list(text),len(text),[],[]
 def debug(*args,**kwargs):
  if not verbose: return
  ss,sd = ' '.join(s),' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<25}]',*args,**kwargs)

 def r1(op):#reduce top of stack, merging ";" as needed''
  if len(d)<(arity:=2-(op in up)): raise ParseError('arity')
  x,k = s.pop(),[d.pop() for _ in range(arity)][::-1]
  debug(f'r1:({x=},{k=})')
  if   x=='lst': x,*k = ('lst',*k[0].children,) if k[0].node=='seq' else k
  elif x=='fun': x,k = k[0],(k[1].children if k[1].node=='seq' else [k[1]])
  elif x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  d.append(Ast(x,*k))

 def reduce_paren():#reduce everything up to open paren, then push AST
  while s and ps[op:=s[-1]]: r1(op)
  r1(op)

 def reduce(p):#reduce with prec<p (but not parens)
  while s and 0<ps[op:=s[-1]]<p: r1(op)

 def balance(op,bal):
  if op in '({[': return bal.append(')}]'['({['.index(op)])
  if op in ')}]' and (not bal or op!=bal.pop()): raise ParseError('unbalanced paren')

 def loop(t,bal,i=0):#advance token, update state
  while True:
   while True:#unary
    if i>=z: return d.append(NIL)
    c = t[i]
    balance(c,bal)
    i += 1
    debug(c,'→')
    if c.isalnum(): d.append(Ast(c))
    elif c==')':
     d.append(NIL)
     reduce_paren()
    elif c==';':
     d.append(NIL)
     s.append(bt[c])
     continue
    elif c in bt and (i>=z or t[i] in ';)'):
     d.append(NIL)
     d.append(NIL)
     s.append(bt[c])
    elif c in ut:
     s.append(ut[c])
     continue
    else: raise ParseError(f'unrecognized token (unary): "{c}"')
    break

   while True:#binary
    if i>=z: return
    c = t[i]
    balance(c,bal)
    i += 1
    debug(c,'↔')
    if c.isalnum():
     s.append('app')
     d.append(Ast(c))
     continue
    elif c==')':
     reduce_paren()
     continue
    elif c in bt:
     reduce(ps[bt[c]])
     s.append(bt[c])
     if i<z and t[i] in ';':
      d.append(NIL)
      continue
    else: raise ParseError(f'unrecognized token (binary): "{c}"')
    break

 bal = []
 loop(t,bal)
 debug('final')
 reduce(max(ps.values())+1)
 if len(bal): raise ParseError('unbalanaced paren')
 if len(d)!=1: raise ParseError(f'data stack: {d}')
 return d.pop()
