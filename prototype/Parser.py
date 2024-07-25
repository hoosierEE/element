from .Ast import Ast
from .Builtin import ADVERB,ASSIGN,CPAREN,ENDEXP,LF,OPAREN,VERB,VERBM,WHITESPACE
import collections as C
NIL = Ast('NIL')
Op = C.namedtuple('Op','name arity')
def _Parse(t:list,verbose:int)->Ast:
 ''' Parse(Scan(str)) ⇒ AST '''
 if not t: return
 z,b,s,d = len(t),[],[],[]
 noun = lambda x:type(x)==tuple or type(x)==str and x.replace('.','').replace('-','').isalnum()

 def debug(*args):#optional logging
  if verbose<1: return
  R = lambda x:'LF' if x==LF else str(x)
  ss = ' '.join(f'{R(x.name)}{"⁰¹²"[x.arity]}' for x in s)
  sd = ' '.join(map(R,d))
  print(f'[{ss:<19}] [{sd:<15}]'+' '.join(map(R,args)))
 def pad(n): (n=='' or n in CPAREN) and d.append(NIL)#()⇒(lst NIL) []⇒(prg NIL) {}⇒(lam NIL)
 def balance(op) -> bool:#incremental parentheses check
  if op in OPAREN: b.append(CPAREN[OPAREN.index(op)]); return 0
  if op in CPAREN and (not b or op!=b.pop()): return 1
 def err(i,m=''): return f'Parse: {m}{LF}{"".join(t[:i]).strip()}'
 def reduce(until:str):#reduce until (until) matches
  while s and str(s[-1].name) not in until: rt(*s.pop())

 def rt(x,arity):#(r)educe (t)op of stack based on x's arity (and precedence)
  k = [d.pop() for _ in range(min(len(d),arity))][::-1]
  if x in ENDEXP:
   if   len(k)>1 and k[1][0]==x: k = [k[0],*k[1][1]]
   elif len(k)>0 and k[0][0]==x: k = [*k[0][1],*k[1:]]
  # if x in ANDOR:           d.append(Ast(x,*k)) #TODO: (and;or) short-circuiting operators
  if noun(x):              d.append(Ast('app',Ast(x),*k))
  elif type(x)==Ast and k: d.append(Ast('app',x,*k))
  else:                    d.append(Ast(x,*k))
  debug('rt',x,k)

 def rp(x:Op):#(r)educe (p)aren, e.g: reduce(OPAREN); rp(s.pop())
  k = Ast(x.name,*(y[1] if (y:=d.pop())[0]==';' else (y,)))
  if x.name=='(' and len(k[1])==1 and k[1][0]!=NIL: k = k[1][0]
  if x.name=='[' and x.arity==2: k = Ast('app',d.pop(),k)
  d.append(k); debug('rp',x,k)

 def rq(k:Ast):#juxtaposition-based syntax: projection and composition
  while s and str(s[-1].name) not in OPAREN+ENDEXP:
   x,a = s.pop()
   k = Ast('cmp',Ast('prj',Ast(x),d.pop()) if a==2 else Ast(x),k)
  d.append(k); debug('rq')

 def loop(i=0) -> int|None:#return index of error-causing token (if any), else None
  nn = lambda i:(t[i+1] if type(t[i+1])==str else 1) if i+1<z else ''
  while True:
   while True:#unary
    if i>=z: return
    c,i,n = t[i],i+1,nn(i); debug(c,'→',n or 'END')
    if balance(c): return i
    if type(c)==tuple: d.append(Ast('vec',*map(Ast,c))); break
    if   c in WHITESPACE and n=='/': return
    if   c in WHITESPACE: continue
    if   c in ENDEXP: d.append(NIL); pad(n); reduce(OPAREN); s.append(Op(';',2))
    elif c in OPAREN: pad(n); s.append(Op(c,1))
    elif c in CPAREN:
     reduce(OPAREN); rp(x:=s.pop());
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: break
    elif c in ADVERB: x = s.pop(); s.append(Op(Ast(c,Ast(x.name)),x.arity)); x.arity==2 and pad(n)
    elif noun(c) or c[0] in '`"': d.append(Ast(c)); break
    elif c in VERB+VERBM and n in CPAREN+ENDEXP:
     d.append(Ast(c)) if s and s[-1].name in OPAREN else rq(Ast('prj',Ast(c))); break
    elif c in VERB+VERBM and n in ADVERB: d.append(Ast(c)); break
    else: s.append(Op(c,1))

   while True:#binary
    if i>=z: return
    c,i,n = t[i],i+1,nn(i); debug(c,'↔',n or 'END')
    if balance(c): return i
    if type(c)==tuple: d.append(Ast('vec',*map(Ast,c))); continue
    if   c in WHITESPACE and n=='/': return
    if   c in WHITESPACE: continue
    if   c in ENDEXP: reduce(OPAREN); pad(n); s.append(Op(';',2))
    elif c in OPAREN: c in "({" and s.append(Op(d.pop(),1)); pad(n); s.append(Op(c,2))
    elif c in CPAREN:
     reduce(OPAREN); rp(x:=s.pop())
     if s and s[-1].name=='{' and x.name=='[' and n!='}': s.append(Op(';',2))
     else: continue
    elif c in ADVERB:
     k = Ast(c,d.pop())#bind adverb to whatever
     while n in ADVERB: k,i,n = Ast(n,k),i+1,nn(i)
     if s:
      debug('adverb')
      if not noun(str(s[-1].name)): s.append(Op(k,1))
      else: d.append(Ast(s.pop().name)); s.append(Op(k,2))
     else: s.append(Op(k,1))
     if s[-1].arity==2: pad(n)
    elif c in ASSIGN:
     if n in CPAREN+ENDEXP: rq(Ast('prj',Ast(c),d.pop())); continue
     else: s.append(Op(c,2))
    elif c in VERBM:
     if n in CPAREN+ENDEXP: raise SyntaxError(err(i,"can't project a prefix op"))
     else: s.append(Op(c,1))
    elif c in VERB:
     if c!='.' and s and s[-1]==Op('.',2): reduce('')#precedence: a.b+1 == (a.b)+1
     if n in CPAREN+ENDEXP: rq(Ast('prj',Ast(c),d.pop())); continue
     else: s.append(Op(c,2))
    else:
     s.append(Op(d.pop(),1))#top of d wasn't a noun after all
     if noun(c) or c[0] in '`"': d.append(Ast(c)); continue
     pad(n); s.append(Op(c,1))
    break

 if i:=loop(): raise SyntaxError(err(i,'unbalanced paren'))
 debug('done'); reduce('')
 while len(d)>1: x=d.pop(); d.append(Ast('app',d.pop(),x))
 if len(d)!=1 or len(s) or len(b): raise SyntaxError(err(z,'leftover stack, maybe unbalanced paren'))
 return d.pop()

def Parse(t:list,verbose:int=0):
 return _Parse(t,verbose)
