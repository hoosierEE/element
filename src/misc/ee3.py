''' https://erikeidt.github.io/The-Double-E-Method
parsing a tiny k-like language:
exprs  ::= expr { ";" expr }
expr   ::= term binary expr | unary expr | term
unary  ::= "-" | "#"
binary ::= "-" | *" | "+"
term   ::= Letter | Number | "(" expr ")"
'''
from Ast import Ast
S = str.split
Z = lambda x,y:dict(zip(x,y))
bc = S('   (   *   +    -  ; ')
bn = S('  fun mul add sub seq')
bp = Z(bn,(0,  1,  1,  1,  2,)) #{name:precedence}
bt = Z(bc,bn) #{token:name}
uc = S('   (    #    - ')
un = S('  lst count neg')
up = Z(un,(2,   1,   1,)) #{name:precedence}
ut = Z(uc,un) #{token:name}
ps = {**bp,**up} #{op:precedence}
pmax = max(ps.values())+1

class ParseError(SyntaxError): pass
def parse(text,verbose=0):
 if not text: return text
 t,z,s,d = list(text),len(text),[],[]
 def debug(*args,**kwargs):
  if not verbose: return
  ss = ' '.join(s)
  sd = ' '.join(repr(x) for x in d)
  print(f'[{ss:<15}] [{sd:<20}]',*args,**kwargs)

 def r1(op):
  '''reduce top of stack, merging ";" as needed'''
  if len(d)<(arity:=2-(op in un)): raise ParseError('arity')
  x,k = s.pop(),[d.pop() for _ in range(arity)][::-1]
  debug(f'r1:({x=},{k=})')
  if   x=='lst': x,*k = ('lst',*k[0].children,) if k[0].node=='seq' else k
  elif x=='fun': x,k = k[0],(k[1].children if k[1].node=='seq' else [k[1]])
  elif x=='seq' and k[1].node==x: k = [k[0],*k[1].children]
  d.append(Ast(x,*k))

 def reduce_paren():
  '''reduce until matching open paren, then push AST'''
  while s and (op:=s[-1]) not in ('fun','lst'):
   r1(op)
  r1(op)

 def reduce(p):
  '''reduce ops with lower precedence (but not parens)'''
  while s and ps[op:=s[-1]]<p and op not in ('fun','lst'):
   r1(op)

 def balance(op,bal):
  '''raise exception if parens are unbalanced'''
  if   op in '({[': bal.append(')}]'['({['.index(op)])
  elif op in ')}]':
   if not bal or op!=bal.pop(): raise ParseError('unbalanced paren')

 def loop(t,bal):
  '''consume tokens, alternating unary/binary states'''
  i = 0
  while True:
   while True: #unary
    if i>=z: return #raise ParseError('end of tokens')
    op = t[i]
    balance(op,bal)
    i += 1
    debug(op,'→')
    if op.isalnum():
     d.append(Ast(op))
     break
    elif op in uc:
     s.append(ut[op])
     continue
    else: raise ParseError(f'unrecognized token (unary): "{op}"')
    break

   while True: #binary
    if i>=z: return #end of tokens
    op = t[i]
    balance(op,bal)
    i += 1
    debug(op,'↔')
    if op==')':
     reduce_paren()
     continue
    elif op in bc:
     reduce(ps[name:=bt[op]])
     s.append(name)
    else: return debug(f'unrecognized token (binary): "{op}"')
    break

 bal = []
 loop(t,bal)
 debug('final')
 reduce(pmax)
 if len(bal): raise ParseError('unbalanaced paren')
 if len(d)!=1: raise ParseError(f'data stack: {d}')
 return d.pop()
