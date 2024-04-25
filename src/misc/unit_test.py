from Parser import Parse
def test_parser(parser):
 x = """
 input      ⇒ expected output (in s-expr form)
            ⇒ None
 # projection/composition/application
 a+         ⇒ (prj + a)
 +-         ⇒ (cmp + (prj -))
 (+)-       ⇒ (prj - +)
 +(-)       ⇒ (+ -)
 1 2+3 4    ⇒ (+ (arr 1 2) (arr 3 4))
 1 2+``a    ⇒ (+ (arr 1 2) (arr ` `a))
 a+-        ⇒ (cmp (prj + a) (prj -))
 *a+-       ⇒ (cmp * (cmp (prj + a) (prj -)))
 +-*        ⇒ (cmp + (cmp - (prj *)))
 a+;        ⇒ (seq (prj + a) NIL)
 (+-)/y     ⇒ ((fld (cmp + (prj -))) y)
 (2+)/y     ⇒ ((fld (prj + 2)) y)
 x(+-)/y    ⇒ ((fld (cmp + (prj -))) x y)
 x(+-*)/y   ⇒ ((fld (cmp + (cmp - (prj *)))) x y)
 x(2+)/y    ⇒ ((fld (prj + 2)) x y)
 ()         ⇒ (lst NIL)
 ()/y       ⇒ ((fld (lst NIL)) y)
 (+)/y      ⇒ ((fld +) y)
 (+/)'y     ⇒ ((ech (fld +)) y)
 +//y       ⇒ ((fld (fld +)) y)
 (+/)/y     ⇒ ((fld (fld +)) y)
 x(+/)y     ⇒ (x ((fld +) y))
 (-a)*b     ⇒ (* (- a) b)
 # lists
 (;)        ⇒ (lst NIL NIL)
 (;b)       ⇒ (lst NIL b)
 (a)        ⇒ a
 (a)b       ⇒ (a b)
 (a;)       ⇒ (lst a NIL)
 (a;;b)     ⇒ (lst a NIL b)
 (a;b)      ⇒ (lst a b)
 (f)/y      ⇒ ((fld f) y)
 *+/y       ⇒ (* ((fld +) y))
 +/y        ⇒ ((fld +) y)
 f[x]/y     ⇒ ((fld (f (prg x))) y)
 +[;;]      ⇒ (+ (prg NIL NIL NIL))
 +[;]       ⇒ (+ (prg NIL NIL))
 +[]        ⇒ (+ (prg NIL))
 +[x;y;z]   ⇒ (+ (prg x y z))
 +[x;y]     ⇒ (+ (prg x y))
 +[x]       ⇒ (+ (prg x))
 --a        ⇒ (- (- a))
 2-3        ⇒ (- 2 3)
 2 - 3      ⇒ (- 2 3)
 2- 3       ⇒ (- 2 3)
 2 -3       ⇒ (arr 2 -3)
 -a         ⇒ (- a)
 ;          ⇒ (seq NIL NIL)
 ;b         ⇒ (seq NIL b)
 []         ⇒ (prg NIL)
 [x]        ⇒ (prg x)
 a          ⇒ a
 a(b)       ⇒ (a b)
 a++b       ⇒ (+ a (+ b))
 a+b        ⇒ (+ a b)
 a+f[x]     ⇒ (+ a (f (prg x)))
 a-b        ⇒ (- a b)
 a-b+c      ⇒ (- a (+ b c))
 a;         ⇒ (seq a NIL)
 a b;       ⇒ (seq (a b) NIL)
 +b;        ⇒ (seq (+ b) NIL)
 a;b;c      ⇒ (seq a b c)
 a;;b       ⇒ (seq a NIL b)
 a;b        ⇒ (seq a b)
 a b        ⇒ (a b)
 a b c      ⇒ (a (b c))
 a b c      ⇒ (a (b c))
 f//y       ⇒ ((fld (fld f)) y)
 f[;]       ⇒ (f (prg NIL NIL))
 f[;y]      ⇒ (f (prg NIL y))
 f[]        ⇒ (f (prg NIL))
 f[()()]    ⇒ (f (prg ((lst NIL) (lst NIL))))
 f[(a)()]   ⇒ (f (prg (a (lst NIL))))
 f[()(a)]   ⇒ (f (prg ((lst NIL) a)))
 f[x;;y]    ⇒ (f (prg x NIL y))
 f[x;]      ⇒ (f (prg x NIL))
 f[x;y]     ⇒ (f (prg x y))
 f[x]       ⇒ (f (prg x))
 x(+)/y     ⇒ ((fld +) x y)
 x(+/)//'y  ⇒ ((ech (fld (fld (fld +)))) x y)
 x(a f/)'y  ⇒ ((ech ((fld f) a NIL)) x y)
 x(f)/y     ⇒ ((fld f) x y)
 x+/y       ⇒ ((fld +) x y)
 x/y        ⇒ ((fld x) y)
 x f//y     ⇒ ((fld (fld f)) x y)
 x f/y      ⇒ ((fld f) x y)
 x{f}/y     ⇒ ((fld (lam f)) x y)
 {()()}     ⇒ (lam ((lst NIL) (lst NIL)))
 {()}       ⇒ (lam (lst NIL))
 {(x)y}     ⇒ (lam (x y))
 {[]()}     ⇒ (lam (prg NIL) (lst NIL))
 {[]a}      ⇒ (lam (prg NIL) a)
 {[]a}      ⇒ (lam (prg NIL) a)
 {[]}       ⇒ (lam (prg NIL))
 {[a];b}    ⇒ (lam (prg a) NIL b)
 {[a]b}     ⇒ (lam (prg a) b)
 {[a]}      ⇒ (lam (prg a))
 {a;b}      ⇒ (lam a b)
 {a b}      ⇒ (lam (a b))
 {f[x]}     ⇒ (lam (f (prg x)))
 {f}/y      ⇒ ((fld (lam f)) y)
 {x(y)}     ⇒ (lam (x y))
 {a f[x]/b} ⇒ (lam ((fld (f (prg x))) a b))
 {a/b}      ⇒ (lam ((fld a) b))
 {x/y}      ⇒ (lam ((fld x) y))
 {x{y}}     ⇒ (lam (x (lam y)))
 {x}        ⇒ (lam x)
 {x}y       ⇒ ((lam x) y)
 {{x}[y]}   ⇒ (lam ((lam x) (prg y)))
 {{}}       ⇒ (lam (lam NIL))
 {}         ⇒ (lam NIL)
 """[1:-1].splitlines()[1:]

 red,end = '\033[91m','\033[0m'
 for i,o in (map(str.strip,a.split('⇒')) for a in x if not a.strip().startswith('#')):
  c = ''#comment
  if '#' in o: o,c = o.split('#')
  try: o,x = o.strip(),parser(i.strip())
  except: print(f'Exception while parsing "{i}"'); continue
  if str(x)==o: continue
  wanted = f'{i} ⇒ {o}{red}{end}'
  actual = f'{"":<{len(i)}}   {red}{x}{end}'
  m = max(len(actual),len(wanted))
  print(f'{wanted:<{m}} ⌈expected⌉ {c}')
  print(f'{actual:<{m}} ⌊ {red}actual{end} ⌋','\n')
