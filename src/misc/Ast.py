class Ast:
 '''node and optional children'''
 def __init__(s,node,*children):
  s.node = node
  s.children = children
 def __repr__(s):
  if not s.children and s.node != 'lis': return f'{s.node}'
  return f'({s.node} {" ".join(map(repr,s.children))})'
