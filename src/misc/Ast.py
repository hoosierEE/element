class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  return f'({s.node} {" ".join(map(repr,s.children))})' if s.children else str(s.node)
