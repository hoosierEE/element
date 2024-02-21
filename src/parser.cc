#include "parser.hpp"

Parser::Parser() {}


bool Parser::error(int line, int pos) {return true;}

bool Parser::parse(std::vector<Token> tok) {
  // First we make a "recognizer".
  // Its job is to return true for valid token sequences.
  // Later, we will construct a parse tree.
  // Each loop through the REPL calls parse(), but we're never guaranteed to
  // have a "complete" program. So given a stream of tokens we parse what we
  // can, and if it can be evaluated, we signal eval() to do something with
  // whatever we have parsed so far.
  token_i = 0;
  while (token_i < tok.size())
    if (not (parse_stmt() or parse_expr()))
      return false;
  return true;
}

bool Parser::match(std::initializer_list<TokenEnum> ts) {
  auto found = std::find(ts.begin(), ts.end(), tokens[token_i].type) == ts.end();
  token_i += found; //advance to next token
  return found;
}

// expr [;\n]
bool Parser::parse_stmt() {
  int p = token_i;
  bool ok = parse_expr() and match({SEMI,LF});
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_expr() {
  return false;
}

// bool Parser::eval(){
//   if (tokenstack.empty() and not instring) {
//     // this->reset();
//   }
//   return false;
// }

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

