from Ast import Ast
import collections as C
NIL = Ast('NIL')
Op = C.namedtuple('Op','name arity')

verb = (*'~!@#$%^&*-_=+|,.<>?','')
copula = ('::',':')
adverb = (*"'/\\",'')
cparen = (*')}]','')
oparen = (*'({[','')
semico = (*';\n','')

def _Parse(t:list,verbose:int)->Ast:#return Ast or None (print errors + info if verbose)
 ''' Parse(Scan(str)) ⇒ AST '''
 if not t: return
 z,b,s,d = len(t),[],[],[]
 noun = lambda x:type(x)==tuple or type(x)==str and x.replace('.','').replace('-','').isalnum()
 def debug(*args):#optional pretty print
  if not verbose: return
  R = lambda x:'LF' if x=='\n' else str(x)
  ss = ' '.join(f'{R(x.name)}{"⁰¹²"[x.arity]}' for x in s)
  sd = ' '.join(map(R,d))
  print(f'[{ss:<19}] [{sd:<15}]',*map(R,args))
 def pad(n): n in cparen and d.append(NIL)#()⇒(lst NIL) []⇒(prg NIL) {}⇒(lam NIL)
 def balance(op) -> bool:#incremental parentheses check
  if op in oparen: b.append(cparen[oparen.index(op)]); return 0
  if op in cparen and (not b or op!=b.pop()): return 1
 def err(i,m=''):
  LF,s = '\n',''.join(t)[:i]
  return f'Parse: {m}{LF}{s.strip()}'

 def reduce(until:str):#reduce until (until) matches
  while s and str(s[-1].name) not in until: rt(*s.pop())

 def rq(k:Ast):#juxtaposition-based syntax: projection and composition
  while s and str(s[-1].name) not in oparen+semico:
   x,a = s.pop()
   k = Ast('cmp',Ast('prj',Ast(x),d.pop()) if a==2 else Ast(x),k)
  d.append(k); debug('rq')

 def rt(x,arity):#(r)educe (t)op of stack based on x's arity
  k = [d.pop() for _ in range(min(len(d),arity))][::-1]
  if x in semico:
   if   len(k)>1 and k[1].node==x: k = [k[0],*k[1].children]
   elif len(k)>0 and k[0].node==x: k = [*k[0].children,*k[1:]]
  if noun(x): d.append(Ast('app',Ast(x),*k))
  elif type(x)==Ast and k:         d.append(Ast('app',x,*k))
  else:                            d.append(Ast(x,*k))
  debug('rt',x,k)

 def rp(x:Op):#(r)educe (p)aren, e.g: reduce(oparen); rp(s.pop())
  k = Ast(x.name,*(y.children if (y:=d.pop()).node==';' else (y,)))
  if x.name=='(' and len(k.children)==1 and k.children[0]!=NIL: k = k.children[0]
  if x.name=='[' and x.arity==2: k = Ast('app',d.pop(),k)
  d.append(k); debug('rp',x,k)

 def loop(i=0) -> int|None:#return error token index or None
  nn = lambda i:(t[i+1] if type(t[i+1])==str else 1) if i+1<z else ''
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,nn(i); debug(c,'→',n or 'END')
    if balance(c): return i
    if type(c)==tuple: d.append(Ast('vec',*map(Ast,c))); break
    if   c==' ' and n=='/': return
    if   c==' ': continue
    if   c in semico: d.append(NIL); pad(n); reduce(oparen); s.append(Op(';',2))
    elif c in oparen: pad(n); s.append(Op(c,1))
    elif c in cparen:
     reduce(oparen); rp(x:=s.pop());
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: break
    elif c in adverb: x = s.pop(); s.append(Op(Ast(c,Ast(x.name)),x.arity)); x.arity==2 and pad(n)
    elif noun(c) or c[0] in '`"': d.append(Ast(c)); break
    elif c[0] in verb and n in cparen+semico:
     if len(c)==2: raise SyntaxError(err(i,"missing argument to unary op"))
     d.append(Ast(c)) if s and s[-1].name in oparen else rq(Ast('prj',Ast(c))); break
    elif c[0] in verb and n in adverb: d.append(Ast(c)); break
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,nn(i); debug(c,'↔',n or 'END')
    if balance(c): return i
    if type(c)==tuple: d.append(Ast('vec',*map(Ast,c))); continue
    if   c==' ': continue
    if   c in semico: reduce(oparen); pad(n); s.append(Op(';',2))
    elif c in oparen: c in "({" and s.append(Op(d.pop(),1)); pad(n); s.append(Op(c,2))
    elif c in cparen:
     reduce(oparen); rp(x:=s.pop())
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: continue
    elif c in adverb:
     k = Ast(c,d.pop())#bind adverb to whatever
     while n and n in adverb: k,i,n = Ast(n,k),i+1,nn(i)
     if s:
      if str(s[-1].name)[0] in verb+oparen: s.append(Op(k,1))
      else: d.append(Ast(s.pop().name)); s.append(Op(k,2))
     else: s.append(Op(k,1))
     if s[-1].arity==2: pad(n)
    elif c in copula and n:
     s.append(Op(c,2))
    elif c in verb:
     if c.endswith(':') and c not in copula:
      if n and n in cparen+semico: rq(Ast('prj',Ast('app',d.pop(),Ast(c))))
      else: s.append(Op(c,1))
      break
     if n in cparen+semico: rq(Ast('prj',Ast(c),d.pop())); continue
     else: s.append(Op(c,2))
    else:
     s.append(Op(d.pop(),1))#whatever this was, it wasn't a noun
     if noun(c) or c[0] in '`"': d.append(Ast(c)); continue
     pad(n); s.append(Op(c,1))
    break

 if i:=loop(): raise SyntaxError(err(i,'unbalanced paren'))
 debug('done'); reduce('')
 while len(d)>1: x=d.pop(); d.append(Ast('app',d.pop(),x))
 if len(d)!=1 or len(s) or len(b): raise SyntaxError(err(z,'leftover stack, maybe unbalanced paren'))
 return d.pop()

def Parse(t:list,verbose:int=0):
 try: return _Parse(t,verbose)
 except SyntaxError as e: print(e)
