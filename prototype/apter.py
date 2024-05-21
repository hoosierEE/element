'''
Apter trees
d: (d)ata
p: (p)arents
'''
from Ast import Ast

### array utils ###


def T(m:list[list])->list[list]:
 '''transpose 2d tensor'''
 a,b = len(m),[len(i) for i in m]; assert 1==len(set(b))
 return [[m[i][j] for i in range(a)] for j in range(b[0])]

def scan(b:'binary_func',x:list,seed=None)->list:
 '''apply binary function b to list, accumulating results (init=x[0])'''
 r = [x[0]] if seed is None else [seed]
 for i in range(1,len(x)): r.append(b(x[i],r[i-1]))
 return r

def sumscan(x:list)->list:
 return scan(lambda a,b:a+b,x)


### "Key" functions ###

def take(d:list,n:list[list])->list[list]:
 '''given depth vector (d), keep first d[i] from each n; pad with 0'''
 r = []
 for a,b in zip(d,n): r.append(b[:a]+[0]*(len(b)-a))
 return r

def bv(d:list[int])->list[list[int]]:
 '''1-hot encode depth vector'''
 m = list(range(1+max(d)))
 c = [[int(i==j) for i in d] for j in m] #columns
 return c

def nd(a:Ast)->tuple[list[str],list[int]]:
 '''return a list of tuples (node,depth) for Ast (a)'''
 def f(a,d,xs,ds):
  match list(a):
   case (x,()): xs.append(x);ds.append(d)
   case (x,ys): xs.append(x);ds.append(d); [f(i,d+1,xs,ds) for i in ys]
 f(a,0,xs:=[],ds:=[])
 return xs,ds

def nc(a:Ast)->list[list[int]]:
 xs,ds = nd(a)
 return take([x+1 for x in ds],T([sumscan(x) for x in bv(ds)]))
