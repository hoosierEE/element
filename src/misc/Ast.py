class Ast:#(node children*)
 def __init__(s,*args): s.node,*s.children = args
 def __repr__(s):
  n = dict(zip("{[(;/\\'",'lam prg lst seq fld scn ech'.split())).get(s.node,s.node)
  return f'({n} {" ".join(map(repr,s.children))})' if s.children else str(n)
