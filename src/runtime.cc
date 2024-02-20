#include "runtime.hpp"
#define addtoken(c) t.push_back({num,i,syntaxmap.at(c),std::string(1,c)})
constexpr bool isdigit(char c){return'0'<=c and c<='9';}
constexpr bool isalpha(char c){return('a'<=c and c<='z')or('A'<=c and c<='Z');}

Runtime::Runtime() {
  currentstring="";
  err=OK;
  instring=false;
  line="";
  linenum=1;
  stringstart=0;
  token_i=0;
  tokens=std::vector<Token>();
  tokenstack=std::stack<char>();
}

bool Runtime::read(std::string line) {
  auto &num = linenum;
  auto &t   = tokens;
  auto &s   = tokenstack;
  auto &st  = instring;
  auto &cs  = currentstring;
  int i;
  int sz = line.size();
  for (i=0;i<sz;i++) {
    char c=line[i];
    // We need to check this before going into the switch(c) below, because
    // strings can contain the begin-comment character, spaces, etc. This "state
    // machine" kind of approach is required here because when we're operating
    // as a REPL, we can't know where the string ends until the user finishes
    // typing.
    if (st) { //we're in the middle of a string
      if (c=='"') { //ah, could this be the end of the string?
        if (cs.back()=='\\') {cs[cs.size()-1]='"';} // nope. a literal double-quote char
        else {t.push_back({num,i,STRING,cs}); st=false; cs="";} // yup. reset
      }
      else {cs += std::string(1,c);}
      continue;
    }

    switch (c) {
    case' ':case'\t':break; // whitespace
    case'"':st=true;break; //begin string
    // case'(':case'[':case'{':addtoken(c);s.push(c);break; //stack ops
    // case'}':if(s.empty()or s.top()!='{'){err=RC;return true;}addtoken(c);s.pop();break;
    // case']':if(s.empty()or s.top()!='['){err=RS;return true;}addtoken(c);s.pop();break;
    // case')':if(s.empty()or s.top()!='('){err=RP;return true;}addtoken(c);s.pop();break;

    // handle 2 character tokens except slash
    case '\'': // eachprior or each
      if (line[i+1]==':') {t.push_back({num,i,STENCIL,"':"}); i++;}
      else {t.push_back({num,i,syntaxmap.at(c),"'"});} break;

    case '\\': // eachleft or backslash
      if(line[i+1]==':') {t.push_back({num,i,EACHLEFT,"\\:"}); i++;}
      else {t.push_back({num,i,syntaxmap.at(c),"\\"});} break;

    case '/': // slash is special
      if (sz==1 or i>1 and line[i-1]==' ') {i=sz-1; break;} // comment continues till end of line
      if (line[i+1]==':') {t.push_back({num,i,EACHRIGHT,"/:"}); i++; break;}
      else {t.push_back({num,i,SLASH,"/"}); break;}

    default: // arbitrary-length tokens
      if (c=='0' and i+1<sz and line[i+1]==':') {t.push_back({num,i,LINES,"0:"}); i++; break;}
      if (c=='1' and i+1<sz and line[i+1]==':') {t.push_back({num,i,BYTES,"1:"}); i++; break;}
      if (isdigit(c)) {// number
        int start = i;            while (i<sz and isdigit(line[i+1])) i++;
        if (line[i+1]=='.') {
          if (not isalpha(line[i+2])) {err=NUMBER; error(); break;}
          i++; /* consume dot */  while (i<sz and isdigit(line[i+1])) i++;
        }
        t.push_back({num,start,NUMBER,line.substr(start,i-start+1)}); break;
      }
      if (isalpha(c)) {// identifiers
        int start = i;            while (i<sz and isalpha(line[i+1])) i++;
        t.push_back({num,start,NAME,line.substr(start,i-start+1)}); break;
      }
      if (syntaxmap.count(c)) {addtoken(c); break;} //other 1-char tokens
      err=UNK; error(); break; //how did you even type that?
    }
  }

  if (st) {cs += "\n";}
  else {t.push_back({num,i,SEP,""});}
  num++;
  return false;
}

// The "essence" of K's grammar:  E:E;e|e e:nve|te| t:n|v v:tA|V n:t[E]|(E)|{E}|N
// brief explanation: https://discord.com/channels/821509511977762827/821511172305846322/1107809632073826374
// There are 5 production rules:
// 1. E:E;e|e
// 2. e:nve|te|ε
// 3. t:n|v
// 4. v:tA|V
// 5. n:t[E]|(E)|{E}|N
// Grammar is defined as
// <nonterminal>:<production>
// | alternates (ε means empty)
// (N)oun non-terminal such as 42 1.9 "xyz" {1+2*x}
// (V)erb primitive such as + or 1:
// (A)dverb ' / \ ': /: \:
// non-terminals:
// (n)oun (v)erb (t)erm
// (e)xpression, singular.
// (E)xpressions, plural. multiple (e) delimited by semicolons

// adapted from https://k.miraheze.org/wiki/Grammar
// Exprs  ::=  (Exprs ";" expr | expr)
// expr   ::=  (noun verb expr | term expr | ε)
// term   ::=  (noun | verb)
// verb   ::=  (term Adverb | Verb)
// noun   ::=  (term "[" Exprs "]" | "(" Exprs ")" | "{" Exprs "}" | Noun)
// Adverb ::=  ['\/] ":"?
// Verb   ::=  (Verb1 ":"? | "0:" | "1:")
// Verb1  ::=  [-:+*%!&|<>=~,^#_$?@.]
// Noun   ::=  (Names | Ints | Floats | String | Symbols)
// Names  ::=  (Names.Name | Name)
// Name   ::=  (Letter | Name Letter | Name Digits)
// Floats ::=  (Float | Floats " " Float)
// Ints   ::=  (Int | Ints " " Int)
// Int    ::=  ("-" Digits | Digits)
// Float  ::=  Int "." Digits
// Strings::=  (String | Strings " " String)
// String ::=  '"' Chars '"'
// Chars  ::=  (Chars Char | ε)
// Char   ::=  ("\0" | "\t" | "\n" | "\r" | '\"' | "\\" | any)
// Symbols::=  ("`" | "`" Name | "`" String)+
// Digits ::=  [0-9]+
// Letter ::=  [A-Za-z]

bool Runtime::parse() {
  // Each loop through the REPL calls parse(), but we're never guaranteed to
  // have a "complete" program. So given a stream of tokens we parse what we
  // can, and if it can be evaluated, we signal eval() to do something with
  // whatever we have parsed so far.
  err = END;
  return parse_stmt() or parse_expr();
}


bool Runtime::match(std::initializer_list<Syntax> ts) {
  auto found = std::find(ts.begin(), ts.end(), tokens[token_i].type) == ts.end();
  token_i += found; //advance to next token
  return found;
}

// expr [;\n]
bool Runtime::parse_stmt() {
  int p = token_i;
  bool ok = parse_expr() and match({SEMI,LF});
  if (!ok) token_i = p;
  return ok;
}

bool Runtime::parse_expr() {
  return false;
}

bool Runtime::eval(){
  if (tokenstack.empty() and not instring) {
    // this->reset();
  }
  return false;
}

void Runtime::print(){
  std::cout << "[tokens]:" << std::endl;;
  for (auto &t : tokens) {
    std::cout << SyntaxRepr[t.type] << "\t" << t.s << std::endl;
  }
}

bool Runtime::error() {
  auto m = err;
  if (m==OK) return false;
  std::cerr << "[ERROR] " << errmsg.at(m) << " [" << linenum << "]" << std::endl;
  std::cerr << line << std::endl;
  err = OK; //reset
  return true;
}
