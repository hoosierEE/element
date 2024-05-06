from Eval import *
from Parser import *
from Scanner import *
def test_expr(scan,parse):
 x = """
 input      ⇒ expected output (in s-expr form)
            ⇒ None
 # projection/composition/application
 a+         ⇒ (prj + a)
 +-         ⇒ (cmp + (prj -))
 (+)-       ⇒ (prj - +)
 +(-)       ⇒ (+ -)
 a:b        ⇒ (: a b)
 (a:)2      ⇒ (app (prj : a) 2)
 a+:        ⇒ None
 (-+:)      ⇒ (cmp - (prj +:))
 -+:        ⇒ (cmp - (prj +:))
 a::b       ⇒ (:: a b)
 1 2+       ⇒ (prj + (vec 1 2))
 1 2+3 4    ⇒ (+ (vec 1 2) (vec 3 4))
 1 2+``a    ⇒ (+ (vec 1 2) (vec ` `a))
 a+-        ⇒ (cmp (prj + a) (prj -))
 *a+-       ⇒ (cmp * (cmp (prj + a) (prj -)))
 +-*        ⇒ (cmp + (cmp - (prj *)))
 a+;        ⇒ (seq (prj + a) NIL)
 (+-)/y     ⇒ (app (fld (cmp + (prj -))) y)
 (2+)/y     ⇒ (app (fld (prj + 2)) y)
 x(+-)/y    ⇒ (app (fld (cmp + (prj -))) x y)
 x(+-*)/y   ⇒ (app (fld (cmp + (cmp - (prj *)))) x y)
 x(2+)/y    ⇒ (app (fld (prj + 2)) x y)
 ()         ⇒ (lst NIL)
 ()/y       ⇒ (app (fld (lst NIL)) y)
 +/         ⇒ (fld +)
 (+/)       ⇒ (fld +)
 (+)/y      ⇒ (app (fld +) y)
 (+/)'y     ⇒ (app (ech (fld +)) y)
 +//y       ⇒ (app (fld (fld +)) y)
 1-+/y      ⇒ (- 1 (app (fld +) y))
 (+/)/y     ⇒ (app (fld (fld +)) y)
 x(+/)y     ⇒ (app x (app (fld +) y))
 (-a)*b     ⇒ (* (- a) b)
 # lists
 (;)        ⇒ (lst NIL NIL)
 (;b)       ⇒ (lst NIL b)
 (a)        ⇒ a
 (a)b       ⇒ (app a b)
 (a;)       ⇒ (lst a NIL)
 (a;;b)     ⇒ (lst a NIL b)
 (a;b)      ⇒ (lst a b)
 (f)/y      ⇒ (app (fld f) y)
 *+/y       ⇒ (* (app (fld +) y))
 +/y        ⇒ (app (fld +) y)
 f[x]/y     ⇒ (app (fld (app f (prg x))) y)
 +[;;]      ⇒ (+ (prg NIL NIL NIL))
 +[;]       ⇒ (+ (prg NIL NIL))
 +[]        ⇒ (+ (prg NIL))
 +[x;y;z]   ⇒ (+ (prg x y z))
 +[x;y]     ⇒ (+ (prg x y))
 +[x]       ⇒ (+ (prg x))
 --a        ⇒ (- (- a))
 (2)-3      ⇒ (- 2 3)
 -(2)-3     ⇒ (- (- 2 3))
 -(2)       ⇒ (- 2)
 +- 1       ⇒ (+ (- 1))
 +-1        ⇒ (+ -1)
 --4        ⇒ (- -4)
 2-3        ⇒ (- 2 3)
 -2 - 3     ⇒ (- -2 3)
 -2- 3      ⇒ (- -2 3)
 -2 -3      ⇒ (vec -2 -3)
 2 - 3      ⇒ (- 2 3)
 2- 3       ⇒ (- 2 3)
 2 -3       ⇒ (vec 2 -3)
 -a         ⇒ (- a)
 ;          ⇒ (seq NIL NIL)
 ;b         ⇒ (seq NIL b)
 []         ⇒ (prg NIL)
 [x]        ⇒ (prg x)
 a          ⇒ a
 a(b)       ⇒ (app a b)
 a++b       ⇒ (+ a (+ b))
 a+b        ⇒ (+ a b)
 a+f[x]     ⇒ (+ a (app f (prg x)))
 a-b        ⇒ (- a b)
 a-b+c      ⇒ (- a (+ b c))
 a;         ⇒ (seq a NIL)
 a b;       ⇒ (seq (app a b) NIL)
 +b;        ⇒ (seq (+ b) NIL)
 a;b;c      ⇒ (seq a b c)
 a;;b       ⇒ (seq a NIL b)
 a;b        ⇒ (seq a b)
 a b        ⇒ (app a b)
 a b c      ⇒ (app a (app b c))
 f//y       ⇒ (app (fld (fld f)) y)
 f[;]       ⇒ (app f (prg NIL NIL))
 f[;y]      ⇒ (app f (prg NIL y))
 f[]        ⇒ (app f (prg NIL))
 f[()()]    ⇒ (app f (prg (app (lst NIL) (lst NIL))))
 f[(a)()]   ⇒ (app f (prg (app a (lst NIL))))
 f[()(a)]   ⇒ (app f (prg (app (lst NIL) a)))
 f[x;;y]    ⇒ (app f (prg x NIL y))
 f[x;]      ⇒ (app f (prg x NIL))
 f[x;y]     ⇒ (app f (prg x y))
 f[x]       ⇒ (app f (prg x))
 x(+)/y     ⇒ (app (fld +) x y)
 x(+/)//'y  ⇒ (app (ech (fld (fld (fld +)))) x y)
 x(a f/)'y  ⇒ (app (ech (app (fld f) a NIL)) x y)
 x(f)/y     ⇒ (app (fld f) x y)
 x+/y       ⇒ (app (fld +) x y)
 x/y        ⇒ (app (fld x) y)
 x f//y     ⇒ (app (fld (fld f)) x y)
 x f/y      ⇒ (app (fld f) x y)
 x{f}/y     ⇒ (app (fld (lam f)) x y)
 {()()}     ⇒ (lam (app (lst NIL) (lst NIL)))
 {()}       ⇒ (lam (lst NIL))
 {(x)y}     ⇒ (lam (app x y))
 {[]()}     ⇒ (lam (prg NIL) (lst NIL))
 {[]a}      ⇒ (lam (prg NIL) a)
 {[]a}      ⇒ (lam (prg NIL) a)
 {[]}       ⇒ (lam (prg NIL))
 {[a];b}    ⇒ (lam (prg a) NIL b)
 {[a]b}     ⇒ (lam (prg a) b)
 {[a]}      ⇒ (lam (prg a))
 {a;b}      ⇒ (lam a b)
 {a b}      ⇒ (lam (app a b))
 {f[x]}     ⇒ (lam (app f (prg x)))
 {f}/y      ⇒ (app (fld (lam f)) y)
 {x(y)}     ⇒ (lam (app x y))
 {a f[x]/b} ⇒ (lam (app (fld (app f (prg x))) a b))
 {x/y}      ⇒ (lam (app (fld x) y))
 {x{y}}     ⇒ (lam (app x (lam y)))
 {x}        ⇒ (lam x)
 {x}y       ⇒ (app (lam x) y)
 {{x}[y]}   ⇒ (lam (app (lam x) (prg y)))
 {{}}       ⇒ (lam (lam NIL))
 {}         ⇒ (lam NIL)
 """[1:-1].splitlines()[1:]

 red,end = '\033[91m','\033[0m'
 for i,o in (map(str.strip,a.split('⇒')) for a in x if not a.strip().startswith('#')):
  c = ''#comment
  if '#' in o: o,c = o.split('#')
  try: o,x = o.strip(),parse(scan(i.strip()),0)#verbosity=0 (silent)
  except: print(f'Exception while parsing "{i}"'); continue
  if str(x)==o: continue
  wanted = f'{i} ⇒ {o}{red}{end}'
  actual = f'{"":<{len(i)}}   {red}{x}{end}'
  m = max(len(actual),len(wanted))
  print(f'{wanted:<{m}} ⌈expected⌉ {c}')
  print(f'{actual:<{m}} ⌊ {red}actual{end} ⌋','\n')


def test_eval(scan,parse,_eval):
 x = """
 input       ⇒ expected output (in s-expr form)
 2           ⇒ 2:i
 2.0         ⇒ 2.0:f
 1,2         ⇒ [1, 2]:I
 1,,2        ⇒ [1, 2]:I
 1,,,2       ⇒ [1, [2]]:L
 ,1 2        ⇒ [[1, 2]]:L
 1 2         ⇒ [1, 2]:I
 1 2.        ⇒ [1.0, 2.0]:F
 a:1 2 3     ⇒ [1, 2, 3]:I
 4,a:1 2 3   ⇒ [4, 1, 2, 3]:L
 4,a:1.0 2 3 ⇒ [4, 1.0, 2.0, 3.0]:L
 """[1:-1].splitlines()[1:]
 for i,o in (map(str.strip,a.split('⇒')) for a in x if not a.strip().startswith('#')):
  c = ''
  if '#' in o: o,c = o.split('#')
  try: o,x = o.strip(),_eval(parse(scan(i.strip()),0))
  except: print(f'Exception evaluating "{i}"'); continue
  if str(x)==o: continue
  print(f'{i} ⇒ {x} (actual)')
  print('expected:',o,)
