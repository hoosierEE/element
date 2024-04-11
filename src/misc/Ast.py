# from dataclasses import dataclass
# @dataclass
class Ast:
 '''(node [children])'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 # def __eq__(s,o):
 #  return s.node==o.node and s.children==o.children
 def __repr__(s):
  n = dict(zip("{[(;/\\'",'lam prg lst seq fld scn ech'.split())).get(s.node,s.node)
  return f'({n} {" ".join(map(repr,s.children))})' if s.children else str(n)
