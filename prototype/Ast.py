class Ast:#(node children*)
 def __init__(s,n,*c): s.node,s.children = s.t = n,c
 def __getitem__(s,i): return s.t[i]
 def __repr__(s):
  n = dict(zip("{[(;/\\'",'lam prg lst seq fld scn ech'.split())).get(s.node,s.node)
  return f'({n} {" ".join(map(repr,s.children))})' if s.children else str(n)
