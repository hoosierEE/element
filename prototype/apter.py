'''
Apter trees
d: (d)ata
p: (p)arents
'''
from Ast import Ast
import pprint

### somewhat more array-oriented-than-python utility functions ###

def T(m:list[list])->list[list]:
 '''transpose 2d (list of lists)'''
 a,b = len(m),[len(i) for i in m]; assert 1==len(set(b))
 return [[m[i][j] for i in range(a)] for j in range(b[0])]

def scan(b:'binary_func',x:list)->list:
 '''
 Accumulate applications of binary function (b) to pairs of
 (accumulator,next_value) for each next value in (x), adding (accumulator) as a
 new element to result (r) with each iteration.

 With some effort, you can implement reduce and map in terms of scan:
 reduce(b,x) == scan(b,x)[-1]
 map(m,x) == scan(lambda _,y:m(y),[0]+x)[1:]
 '''
 r = [x[0]]
 for i in range(1,len(x)): r.append(b(x[i],r[i-1]))
 return r

def sumscan(x:list)->list:
 return scan(lambda a,b:a+b,x)


### "Key" functions ###

def take(d:list[int],n:list[list[int]])->list[list[int]]:
 '''Given depth vector (d), keep first d_i from each n. Pad with 0'''
 return [b[:a]+[0]*(len(b)-a) for a,b in zip(d,n)]

def copy_if(d:list[bool],n:list[list[int]])->list[list[int]]:
 '''keep elements from n where d is true'''
 return [b for a,b in zip(d,n) if a]

def bv(d:list[int])->list[list[int]]:
 '''1-hot encode depth vector'''
 return [[int(i==j) for i in d] for j in range(1+max(d))] #columns

def nd(a:Ast)->tuple[list[str],list[int]]:
 '''([node],[depth]) for Ast (a)'''
 def f(a,d,xs,ds):
  match list(a):
   case (x,()): xs.append(x); ds.append(d)
   case (x,ys): xs.append(x); ds.append(d); [f(i,d+1,xs,ds) for i in ys]
 f(a,0,xs:=[],ds:=[])
 return xs,ds

def nc(n:list[list[int]],d:list[int],debug:bool=False)->list[list[int]]:
 '''Ast ⇒ node coordinates'''
 if debug:
  return list(zip(take([x+1 for x in d],T([sumscan(x) for x in bv(d)])),n))
 return take([x+1 for x in d],T([sumscan(x) for x in bv(d)]))

def is_ancestor(a,b)->int:
 '''
 Is (a) an ancestor of (b)?
 is_ancestor([1,1,0,0],[1,2,0,0]) == True
 '''
 return all(int(i==j or i==0) for i,j in zip(a,b))

def key(k,*v):
 '''collect items from (v) by their corresponding key (k)'''
 r = {repr(ki):[] for ki in k}
 for i,*j in zip(k,*v):
  r[repr(i)].append(j)
 return r

def apter(n,t,d,X):
 Fc = nc(n,d) # get node coordinates
 Fcp = take(d,Fc) # take all but last non-zero element while keeping original shape:
 Fp = copy_if([x==X for x in t],Fc) # get function node keys
 Fb = [[int(is_ancestor(x,y)) for x in Fp] for y in Fcp] # ancestor locations (1-hot)
 Fi = [max([a*b for a,b in zip(x,range(len(x)))]) for x in Fb] #ancestor index (int)
 Fk = [Fp[i] for i in Fi] # ancestor at each index
 pp = pprint.PrettyPrinter(depth=4)
 pp.pprint(key(Fk,d,n,Fc))

if __name__ == "__main__":
 # {{⍵+⍵}7}
 n,t,d = [*'f000ω+ω07'],[*'FEFEVPVAN'],[0,1,2,3,4,4,4,2,3]
 apter(n,t,d,'F')

 # v←(a+b)÷c×d
 n,t,d = [*'v0a+b%0c*d'],[*'EEVPVPEVPV'],[0,1,2,2,2,1,1,2,2,2]
 apter(n,t,d,'E')
