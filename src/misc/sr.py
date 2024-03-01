# shift-reduce parser experiment in python, based on here:
# https://www.geeksforgeeks.org/shift-reduce-parser-compiler/
rules = {
 "S": ("(L)","a"),
 "L": ("L,S","S"),
}
rrule = {ki:k for k,v in rules.items() for ki in v}
def test(seq):
 print('---',seq,'---')
 stk = []
 for t in seq:
  if t in ",a()":
   stk.append(t)
   print(' : '+''.join(stk))

  while True:
   s = ''.join(stk)
   for r in rrule:
    if s.endswith(r):
     stk = stk[:-len(r)]
     stk.append(rrule[r])
     break
   print('r: '+s)
   if s == ''.join(stk):
    break

 ok = len(stk) == 1 and stk[0] in rules
 print('pass' if ok else 'fail')
 return ok

assert test('(a,(a,a))')
assert test('a')
assert test('(a,(a,(a),a,(a,a)))')
assert not test('(a,)')
assert not test('()')
