def unit(parse):
 x = """
 input     ⇒ expected output (in s-expr form)
           ⇒ None
 ()        ⇒ (lst NIL)
 (+)/y     ⇒ ((fld +) y)
 (+/)'y    ⇒ ((ech ((fld +) NIL)) y)
 (-a)*b    ⇒ (* (- a) b)
 (;)       ⇒ (lst NIL NIL)
 (;b)      ⇒ (lst NIL b)
 (a)       ⇒ a
 (a)b      ⇒ (a b)
 (a;)      ⇒ (lst a NIL)
 (a;;b)    ⇒ (lst a NIL b)
 (a;b)     ⇒ (lst a b)
 (f)/y     ⇒ ((fld f) y)
 *+/y      ⇒ (* ((fld +) y))
 +/y       ⇒ ((fld +) y)
 +[;;]     ⇒ (+ (prg NIL NIL NIL))
 +[;]      ⇒ (+ (prg NIL NIL))
 +[]       ⇒ (+ (prg NIL))
 +[x;y;z]  ⇒ (+ (prg x y z))
 +[x;y]    ⇒ (+ (prg x y))
 +[x]      ⇒ (+ (prg x))
 --a       ⇒ (- (- a))
 -a        ⇒ (- a)
 ;         ⇒ (seq NIL NIL)
 ;b        ⇒ (seq NIL b)
 []        ⇒ (prg NIL)
 [x]       ⇒ (prg x)
 a         ⇒ a
 a(b)      ⇒ (a b)
 a++b      ⇒ (+ a (+ b))
 a+b       ⇒ (+ a b)
 a+f[x]    ⇒ (+ a (fun f x))
 a-b       ⇒ (- a b)
 a-b+c     ⇒ (- a (+ b c))
 a;        ⇒ (seq a NIL)
 a;;b      ⇒ (seq a NIL b)
 a;b       ⇒ (seq a b)
 ab        ⇒ (a b)
 abc       ⇒ (a (b c))
 abc       ⇒ (a (b c))
 f//y      ⇒ ((fld (fld f)) y)
 f[;]      ⇒ (fun f NIL NIL)
 f[;y]     ⇒ (fun f NIL y)
 f[]       ⇒ (fun f NIL)
 f[x;;y]   ⇒ (fun f x NIL y)
 f[x;]     ⇒ (fun f x NIL)
 f[x;y]    ⇒ (fun f x y)
 f[x]      ⇒ (fun f x)
 x(+)/y    ⇒ ((fld +) x y)
 x(+/)//'y ⇒ ((ech (fld (fld ((fld +) NIL)))) x y)
 x(af/)'y  ⇒ ((ech ((fld f) a NIL)) x y)
 x(f)/y    ⇒ ((fld f) x y)
 x+/y      ⇒ ((fld +) x y)
 x/y       ⇒ ((fld x) y)
 xf//y     ⇒ ((fld (fld f)) x y)
 xf/y      ⇒ ((fld f) x y)
 x{f}/y    ⇒ ((fld (lam f)) x y)
 {()()}    ⇒ (lam ((lst NIL) (lst NIL)))
 {()}      ⇒ (lam (lst NIL))
 {(x)y}    ⇒ (lam (x y))
 {[]()}    ⇒ (lam (prg NIL) (lst NIL))
 {[]a}     ⇒ (lam (prg NIL) a)
 {[]a}     ⇒ (lam (prg NIL) a)
 {[]}      ⇒ (lam (prg NIL))
 {[a];b}   ⇒ (lam (prg a) NIL b)
 {[a]b}    ⇒ (lam (prg a) b)
 {[a]}     ⇒ (lam (prg a))
 {a;b}     ⇒ (lam a b)
 {ab}      ⇒ (lam (a b))
 {f[x]}    ⇒ (lam (fun f x))
 {f}/y     ⇒ ((fld (lam f)) y)
 {x(y)}    ⇒ (lam (x y))
 {x/y}     ⇒ (lam ((fld x) y))
 {x{y}}    ⇒ (lam (x (lam y)))
 {x}       ⇒ (lam x)
 {x}y      ⇒ ((lam x) y)
 {{x}[x]}  ⇒ (lam (fun (lam x) x))
 {{}}      ⇒ (lam (lam NIL))
 {}        ⇒ (lam NIL)
 """[1:-1].splitlines()[1:]

 red,end = '\033[91m','\033[0m'
 for i,o in (map(str.strip,a.split('⇒')) for a in x):
  if i and i[0]=='#': continue
  c = ''#comment
  if '#' in o: o,c = o.split('#')
  try: x = parse(i.strip())
  except: print(f'Exception while parsing "{i}"'); continue
  if str(x)!=o.strip():
   wanted = f'{i} ⇒ {o}{red}{end}'
   actual = f'{"":<{len(i)}}   {red}{x}{end}'
   m = max(len(actual),len(wanted))
   print(f'{wanted:<{m}} ⌈expected⌉ {c}')
   print(f'{actual:<{m}} ⌊ {red}actual{end} ⌋','\n')
