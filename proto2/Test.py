from .Parser import Parse
from .Scanner import Scan

def test_expr(scan,parse):
 x = """
 input      ⇒ expected output (in s-expr form)
            ⇒ None
 #
 # projection/composition/application
 #
 a+         ⇒ (prj + a)
 +-         ⇒ (cmp + (prj -))
 (+)-       ⇒ (prj - +)
 +(-)       ⇒ (+ -)
 a:b        ⇒ (: a b)
 (a:)2      ⇒ (app (prj : a) 2)
 (-+:)      ⇒ (cmp - (prj +:))
 -+:        ⇒ (cmp - (prj +:))
 a::b       ⇒ (:: a b)
 a:f/y      ⇒ (: a (app (/ f) y))
 1 2+       ⇒ (prj + (vec 1 2))
 1 2+3 4    ⇒ (+ (vec 1 2) (vec 3 4))
 1 2+``a    ⇒ (+ (vec 1 2) (vec ` `a))
 a b 1 2    ⇒ (app a (app b (vec 1 2)))
 1 2 a 3 4  ⇒ (app (vec 1 2) (app a (vec 3 4)))
 a+-        ⇒ (cmp (prj + a) (prj -))
 *a+-       ⇒ (cmp * (cmp (prj + a) (prj -)))
 +-*        ⇒ (cmp + (cmp - (prj *)))
 a+;        ⇒ (; (prj + a) ∅)
 (+-)/y     ⇒ (app (/ (cmp + (prj -))) y)
 (2+)/y     ⇒ (app (/ (prj + 2)) y)
 x(+-)/y    ⇒ (app (/ (cmp + (prj -))) x y)
 x(+-*)/y   ⇒ (app (/ (cmp + (cmp - (prj *)))) x y)
 x(2+)/y    ⇒ (app (/ (prj + 2)) x y)
 ()         ⇒ (⋯ ∅)
 ()/y       ⇒ (app (/ (⋯ ∅)) y)
 +/         ⇒ (/ +)
 (+/)       ⇒ (/ +)
 (+)/y      ⇒ (app (/ +) y)
 (+/)'y     ⇒ (app (' (/ +)) y)
 +//y       ⇒ (app (/ (/ +)) y)
 1-+/y      ⇒ (- 1 (app (/ +) y))
 (+/)/y     ⇒ (app (/ (/ +)) y)
 x(+/)y     ⇒ (app x (app (/ +) y))
 (-a)*b     ⇒ (* (- a) b)
 #
 # dicts
 #
 [a:1; b:2] ⇒ ([ (: a 1) (: b 2))
 `a`b!1 2   ⇒ (! (vec `a `b) (vec 1 2))
 #
 # lists
 #
 (;)        ⇒ (⋯ ∅ ∅)
 (;b)       ⇒ (⋯ ∅ b)
 (a)        ⇒ a
 (a)b       ⇒ (app a b)
 (a;)       ⇒ (⋯ a ∅)
 (a;;b)     ⇒ (⋯ a ∅ b)
 (a;b)      ⇒ (⋯ a b)
 (f)/y      ⇒ (app (/ f) y)
 *+/y       ⇒ (* (app (/ +) y))
 +/y        ⇒ (app (/ +) y)
 f[x]/y     ⇒ (app (/ (app f ([ x))) y)
 +[;;]      ⇒ (+ ([ ∅ ∅ ∅))
 +[;]       ⇒ (+ ([ ∅ ∅))
 +[]        ⇒ (+ ([ ∅))
 +[x;y;z]   ⇒ (+ ([ x y z))
 +[x;y]     ⇒ (+ ([ x y))
 +[x]       ⇒ (+ ([ x))
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
 ;          ⇒ (; ∅ ∅)
 ;b         ⇒ (; ∅ b)
 []         ⇒ ([ ∅)
 [x]        ⇒ ([ x)
 a.b.c      ⇒ (. a (. b c))
 a.b - 1    ⇒ (- (. a b) 1)
 1 - a.b    ⇒ (- 1 (. a b))
 a          ⇒ a
 a(b)       ⇒ (app a b)
 a++b       ⇒ (+ a (+ b))
 a+b        ⇒ (+ a b)
 a+f[x]     ⇒ (+ a (app f ([ x)))
 a-b        ⇒ (- a b)
 a-b+c      ⇒ (- a (+ b c))
 a;         ⇒ (; a ∅)
 a b;       ⇒ (; (app a b) ∅)
 +b;        ⇒ (; (+ b) ∅)
 a;b;c      ⇒ (; a b c)
 a;;b       ⇒ (; a ∅ b)
 a;b        ⇒ (; a b)
 a b        ⇒ (app a b)
 a b c      ⇒ (app a (app b c))
 f//y       ⇒ (app (/ (/ f)) y)
 f[;]       ⇒ (app f ([ ∅ ∅))
 f[;y]      ⇒ (app f ([ ∅ y))
 f[]        ⇒ (app f ([ ∅))
 f[()()]    ⇒ (app f ([ (app (⋯ ∅) (⋯ ∅))))
 f[(a)()]   ⇒ (app f ([ (app a (⋯ ∅))))
 f[()(a)]   ⇒ (app f ([ (app (⋯ ∅) a)))
 f[x;;y]    ⇒ (app f ([ x ∅ y))
 f[x;]      ⇒ (app f ([ x ∅))
 f[x;y]     ⇒ (app f ([ x y))
 f[x]       ⇒ (app f ([ x))
 x(+)/y     ⇒ (app (/ +) x y)
 x(+/)//'y  ⇒ (app (' (/ (/ (/ +)))) x y)
 x(a f/)'y  ⇒ (app (' (app (/ f) a ∅)) x y)
 x(f)/y     ⇒ (app (/ f) x y)
 x+/y       ⇒ (app (/ +) x y)
 x/y        ⇒ (app (/ x) y)
 x f//y     ⇒ (app (/ (/ f)) x y)
 x f/y      ⇒ (app (/ f) x y)
 x{f}/y     ⇒ (app (/ (λ f)) x y)
 #
 # lambdas
 #
 {()()}     ⇒ (λ (app (⋯ ∅) (⋯ ∅)))
 {()}       ⇒ (λ (⋯ ∅))
 {(x)y}     ⇒ (λ (app x y))
 {[]()}     ⇒ (λ ([ ∅) (⋯ ∅))
 {[]a}      ⇒ (λ ([ ∅) a)
 {[]a}      ⇒ (λ ([ ∅) a)
 {[]}       ⇒ (λ ([ ∅))
 {[a];b}    ⇒ (λ ([ a) ∅ b)
 {[a]b}     ⇒ (λ ([ a) b)
 {[a]}      ⇒ (λ ([ a))
 {a;b}      ⇒ (λ a b)
 {a b}      ⇒ (λ (app a b))
 {f[x]}     ⇒ (λ (app f ([ x)))
 {f}/y      ⇒ (app (/ (λ f)) y)
 {x(y)}     ⇒ (λ (app x y))
 {a f[x]/b} ⇒ (λ (app (/ (app f ([ x))) a b))
 {x/y}      ⇒ (λ (app (/ x) y))
 {x{y}}     ⇒ (λ (app x (λ y)))
 {x}        ⇒ (λ x)
 {x}y       ⇒ (app (λ x) y)
 {{x}[y]}   ⇒ (λ (app (λ x) ([ y)))
 {{}}       ⇒ (λ (λ ∅))
 {}         ⇒ (λ ∅)
 """[1:-1].splitlines()[1:]

 red,end = '\033[91m','\033[0m'
 ok,total = 0,0
 for i,o in (map(str.strip,a.split('⇒')) for a in x if not a.strip().startswith('#')):
  total += 1
  c = ''#comment
  if '#' in o: o,c = o.split('#')
  try: o,x = o.strip(),parse(scan(i.strip()),0); ok += 1
  except: print(f'Exception while parsing "{i}"'); continue
  if str(x)==o: continue
  wanted = f'{i} ⇒ {o}{red}{end}'
  actual = f'{"":<{len(i)}}   {red}{x}{end}'
  m = max(len(actual),len(wanted))
  print(f'{wanted:<{m}} ⌈expected⌉ {c}')
  print(f'{actual:<{m}} ⌊ {red}actual{end} ⌋','\n')


def test_exception(scan,parse):
 x = """
 a+:
 (a+:)
 ())
 """[1:-1].splitlines()
 for i in map(str.strip,x):
  try:
   parse(scan(i))
   raise SyntaxError(f"Should have raised SyntaxError, but didn't: {i}")
  except SyntaxError: continue


def test_eval(scan,parse,evil):
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
 4,a:1 2 3   ⇒ [4, 1, 2, 3]:I
 4,a:1.0 2 3 ⇒ [4, 1.0, 2.0, 3.0]:L
 """[1:-1].splitlines()[1:]
 ok,total = 0,0
 for i,o in (map(str.strip,a.split('⇒')) for a in x if not a.strip().startswith('#')):
  total += 1
  c = ''
  if '#' in o: o,c = o.split('#')
  try:
   o,x = o.strip(),evil(parse(scan(i.strip()),0))
   ok += 1
  except Exception as e:
   print(f'Exception ({e}) evaluating "{i}"')
   continue
  if str(x)==o: continue
  print(f'{i} ⇒ {x} (actual)')
  print(f'{"expected:":>{len(i)}}   {o}')


# def test_all(scan,parse,evil):
#  print("test_expr:")
#  test_expr(scan,parse)
#  print("test_exception:")
#  test_exception(scan,parse)
#  print("test_eval:")
#  test_eval(scan,parse,evil)
