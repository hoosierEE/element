import collections as C
class Ast:#(node [children])
 def __init__(s,*args): s.node,*s.children = args
 def __repr__(s):
  n = dict(zip("{[(;/\\'",'lam prg lst seq fld scn ech'.split())).get(s.node,s.node)
  return f'({n} {" ".join(map(repr,s.children))})' if s.children else str(n)

NIL,Op = Ast('NIL'),C.namedtuple('Op','name arity')
verb,adverb,cparen,oparen,semico = '~!@#$%^&*-_=+|:,.<>?',"'/\\",')}]','({[',';'

def parse(t:str,verbose:int=0)->Ast:
 if not t: return
 t,z,b,s,d = list(t),len(t),[],[],[]

 def debug(*args):
  if not verbose: return
  ss = ' '.join(f'{x.name}{"⁰¹²"[x.arity]}' for x in s)
  sd = ' '.join(map(str,d))
  print(f'[{ss:<19}] [{sd:<15}]',*args)

 def pad(n): n in cparen and d.append(NIL)

 def balance(op):
  if op in oparen: b.append(cparen[oparen.index(op)]); return
  if op in cparen and (not b or op!=b.pop()): return 1

 def reduce(until:str):
  while s and str(s[-1].name) not in until: rt(*s.pop())

 def rq(k:Ast):#handle juxtaposition-based projections and copmositions
  while s and str(s[-1].name) not in oparen+semico:
   x,a = s.pop(); k = Ast('cmp',Ast('prj',Ast(x),d.pop()) if a==2 else Ast(x),k)
  d.append(k); debug('rq')

 def rt(x,arity):#(r)educe (t)op of stack based on x's arity
  k = [d.pop() for _ in range(min(len(d),arity))][::-1]
  if x==';':
   if   len(k)>1 and k[1].node==x: k = [k[0],*k[1].children]
   elif len(k)>0 and k[0].node==x: k = [*k[0].children,*k[1:]]
  d.append(Ast(x,*k)); debug('rt',x,k)

 def rp(x:Op):#(r)educe (p)aren, e.g: reduce(oparen); rp(s.pop())
  k = Ast(x.name,*(y.children if (y:=d.pop()).node==';' else (y,)))
  if x.name=='(' and len(k.children)==1 and k.children[0]!=NIL: k = k.children[0]
  if x.name=='[' and x.arity==2: k = Ast(d.pop(),k)
  d.append(k); debug('rp',x,k)

 def loop(i=0):
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; debug(c,'→',n or 'END')
    if balance(c): return i
    if   c in semico: d.append(NIL); pad(n); reduce(oparen); s.append(Op(c,2))
    elif c in oparen: pad(n); s.append(Op(c,1))
    elif c in cparen:
     reduce(oparen); rp(x:=s.pop());
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: break
    elif c in adverb: x = s.pop(); s.append(Op(Ast(c,Ast(x.name)),x.arity)); x.arity==2 and pad(n)
    elif c.isalnum(): d.append(Ast(c)); break
    elif c in verb and n in cparen+semico:
     d.append(Ast(c)) if s and s[-1].name in oparen else rq(Ast('prj',Ast(c))); break
    elif c in verb and n in adverb: d.append(Ast(c)); break
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,t[i+1]if i+1<z else''; debug(c,'↔',n or 'END')
    if balance(c): return i
    if   c in semico: reduce(oparen); pad(n); s.append(Op(c,2))
    elif c in oparen: c in "({" and s.append(Op(d.pop(),2)); pad(n); s.append(Op(c,2))
    elif c in cparen:
     reduce(oparen); rp(x:=s.pop())
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: continue
    elif c in adverb:
     k = Ast(c,d.pop())#bind adverb to whatever
     while n and n in adverb: k,i,n = Ast(n,k),i+1,t[i+1]if i+1<z else''
     if s:
      if str(s[-1].name) in verb+oparen:
       if d: s.append(Op(d.pop(),1))
       s.append(Op(k,1))
      else: d.append(Ast(s.pop().name)); s.append(Op(k,2))
     else: s.append(Op(k,2))
     if s[-1].arity==2: pad(n)
    elif c in verb:
     if n in cparen+semico: rq(Ast('prj',Ast(c),d.pop())); continue
     else: s.append(Op(c,2))
    else:
     s.append(Op(str(d.pop()),1))
     if c.isalnum(): d.append(Ast(c)); continue
     pad(n); s.append(Op(c,1))
    break

 if i:=loop(): return print('unbalanced paren: '+"".join(t)+'\n'+f'{"^":>{18+i}}')
 debug('done'); reduce('')
 while len(d)>1: x=d.pop(); d.append(Ast(d.pop(),x))
 if len(d)!=1 or len(s) or len(b): return SyntaxError("ERROR: stacks should end up empty")
 return d.pop()
