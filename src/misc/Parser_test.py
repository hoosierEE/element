def unit(parse):
 x = """
 input     ‥ expected output
 {x{y}}    ‥ (lam (x (lam y)))
 {x(y)}    ‥ (lam (x y))
 {(x)y}    ‥ (lam (x y))
 {()}      ‥ (lam (lst NIL))
 {()()}    ‥ (lam ((lst NIL) (lst NIL)))
 {[]a}     ‥ (lam (prg NIL) a)
 {[]()}    ‥ (lam (prg NIL) (lst NIL))
           ‥ None
 abc       ‥ (a (b c))
 ab        ‥ (a b)
 a(b)      ‥ (a b)
 (a)b      ‥ (a b)
 abc       ‥ (a (b c))
 a         ‥ a
 -a        ‥ (- a)
 --a       ‥ (- (- a)) # NOTE: pushing to operand stack at wrong time
 a-b       ‥ (- a b)
 a-b+c     ‥ (- a (+ b c))
 ()        ‥ (lst NIL)
 (a)       ‥ a
 (a;b)     ‥ (lst a b)
 (;b)      ‥ (lst NIL b)
 (a;)      ‥ (lst a NIL)
 (;)       ‥ (lst NIL NIL)
 (a;;b)    ‥ (lst a NIL b)
 a;b       ‥ (seq a b)
 ;b        ‥ (seq NIL b)
 a;        ‥ (seq a NIL)
 ;         ‥ (seq NIL NIL)
 a;;b      ‥ (seq a NIL b)
 a+b       ‥ (+ a b)
 a++b      ‥ (+ a (+ b))
 []        ‥ (prg NIL)
 [x]       ‥ (prg x)
 f[]       ‥ (fun f NIL)
 f[x]      ‥ (fun f x)
 f[x;y]    ‥ (fun f x y)
 f[;y]     ‥ (fun f NIL y)
 f[x;]     ‥ (fun f x NIL)
 f[;]      ‥ (fun f NIL NIL)
 f[x;;y]   ‥ (fun f x NIL y)
 a+f[x]    ‥ (+ a (fun f x))
 +[]       ‥ (+ (prg NIL)) # comment out this test for now
 +[x]      ‥ (+ (prg x))
 +[x;y]    ‥ (+ (prg x y))
 +[x;y;z]  ‥ (+ (prg x y z))
 +[;]      ‥ (+ (prg NIL NIL))
 +[;;]     ‥ (+ (prg NIL NIL NIL))
 {}        ‥ (lam NIL)
 {x}       ‥ (lam x)
 {[]}      ‥ (lam (prg NIL))
 {[a]}     ‥ (lam (prg a))
 {[]a}     ‥ (lam (prg NIL) a)
 {[a]b}    ‥ (lam (prg a) b)
 {[a];b}   ‥ (lam (prg a) NIL b)
 {a;b}     ‥ (lam a b)
 {ab}      ‥ (lam (a b))
 {x/y}     ‥ (lam ((fld x) y))
 {{}}      ‥ (lam (lam NIL))
 {f[x]}    ‥ (lam (fun f x))
 {x}y      ‥ ((lam x) y)
 {{x}[x]}  ‥ (lam (fun (lam x) x))
 x/y       ‥ ((fld x) y)
 +/y       ‥ ((fld +) y)
 {f}/y     ‥ ((fld (lam f)) y)
 x{f}/y    ‥ ((fld (lam f)) x y)
 x+/y      ‥ ((fld +) x y)
 xf/y      ‥ ((fld f) x y)
 (f)/y     ‥ ((fld f) y)
 x(f)/y    ‥ ((fld f) x y)
 (+)/y     ‥ ((fld +) y)
 x(+)/y    ‥ ((fld +) x y)
 (-a)*b    ‥ (* (- a) b)
 f//y      ‥ ((fld (fld f)) y)
 xf//y     ‥ ((fld (fld f)) x y)
 (+/)'y   ‥ (ech ((fld +) NIL) y)
 x(+/)//'y ‥ (ech (fld (fld (fld +))) x y)
 x(af/)'y  ‥ ((ech ((fld f) a NIL)) x y)
 """[1:-1].splitlines()[1:]
 red,end = '\033[91m','\033[0m'
 for i,o in (map(str.strip,a.split('‥')) for a in x):
  if i and i[0]=='#': continue
  c = ''#comment
  if '#' in o: o,c = o.split('#')
  try: x = parse(i.strip())
  except: print(f'Exception while parsing "{i}"')
  if str(x)!=o.strip():
   wanted = f'{i} ⇒ {o}{red}{end}'
   actual = f'{"":<{len(i)}}   {red}{x}{end}'
   m = max(len(actual),len(wanted))
   print(f'{wanted:<{m}} ⌈expected⌉ {c}')
   print(f'{actual:<{m}} ⌊ {red}actual{end} ⌋','\n')
