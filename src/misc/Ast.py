class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  nodename = {'{':'lam','[':'prg','(':'lst'}.get(s.node,s.node)
  return f'({nodename} {" ".join(map(repr,s.children))})' if s.children else str(s.node)
