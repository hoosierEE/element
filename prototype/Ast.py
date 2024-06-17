class Ast:#(node,*children)
 def __init__(s,n,*c):
  s.node = n
  s.children = c
  s.t = n,c
 def __iter__(s): return iter(s.t)
 def __getitem__(s,i): return s.t[i]
 def __repr__(s):
  a,b=s;n=dict(zip("{[(;/\\'",'lam prg lst seq fld scn ech'.split())).get(a,a)
  return f'({n} {" ".join(map(repr,s[1]))})' if b else str(n) # lisp-style
  # return f'{n} ({", ".join(map(repr,s[1]))})' if b else str(n) # C-style
  # return f'{" ".join(map(repr,s[1]))} {n}({len(s[1])})' if b else str(n) # rpn
