#include "parser.hpp"
#include <iostream>
// The "essence" of K's grammar:  E:E;e|e e:nve|te| t:n|v v:tA|V n:t[E]|(E)|{E}|N
// brief explanation: https://discord.com/channels/821509511977762827/821511172305846322/1107809632073826374
// Below is adapted from https://k.miraheze.org/wiki/Grammar
// Exprs  ::=  expr (";" expr)*
// expr   ::=  noun verb expr | term expr | ""
// term   ::=  noun | verb
// verb   ::=  term Adverb | Verb
// noun   ::=  term "[" Exprs "]" | "(" Exprs ")" | "{" Exprs "}" | Noun
// Adverb ::=  ['\/] ":"?
// Verb   ::=  Verb1 ":"? | "0:" | "1:"
// Verb1  ::=  [-:+*%!&|<>=~,^#_$?@.]
// Noun   ::=  Names | Ints | Floats | String | Symbols
// Names  ::=  Name ("." Name)*
// Name   ::=  [A-Za-z][A-Za-z0-9]*
// Floats ::=  Float (" " Float)*
// Ints   ::=  Int (" " Int)*
// Int    ::=  "-"? Digits
// Float  ::=  Int "." Digits
// Strings::=  String (" " String)*
// String ::=  '"' (Char)* '"'
// Char   ::=  "\0" | "\t" | "\n" | "\r" | '\"' | "\\" | any
// Symbols::=  ("`" | "`" Name | "`" String)+
// Digits ::=  [0-9]+

// Exprs  ::=  expr (";" expr)*
// expr   ::=  noun verb expr | term expr | ""  ///NOTE: (n v | t)*
// term   ::=  noun | verb
// verb   ::=  term "A" | "V"
// noun   ::=  "N" | term "[" Exprs "]" | "(" Exprs ")" | "{" Exprs "}"

// expr ::= (noun verb expr | term expr)?
// // remove left recursion:
// // expr1 ::= noun verb expr2
// // expr2 ::= term expr2 | ε
// term ::= noun | verb
// verb ::= term "/" | "V"
// noun ::= term "[" expr "]" | "(" expr ")" | "{" expr "}"


// TODO
bool Parser::error(int line, int pos) {
  return token_i == tokens.size();
}

bool Parser::ints() {return true;}
bool Parser::floats() {return true;}
bool Parser::symbols() {return true;}
bool Parser::strings() {return true;}
// END TODO

Parser::Parser() {}
bool Parser::parse(std::vector<Token> ts) {
  tokens = ts;
  token_i = 0;
  return exprs();
}

bool Parser::eat(TokenEnum t) {
  if (token_i < tokens.size() and t == tokens[token_i].type) {
    token_i++;
    return true;
  }
  return false;
}

bool Parser::match(std::initializer_list<TokenEnum> ts) {
  std::cout << token_i << " " << tokens.size() << std::endl;
  if (token_i < tokens.size() and std::find(ts.begin(),ts.end(),tokens[token_i].type) == ts.end()) {
    token_i++;
    return true;
  }
  return false;
}

// bool Parser::exprs() {return expr() and expr_s();}
bool Parser::exprs() {return true and expr_s();}
bool Parser::expr() {return nve() or te();}
bool Parser::expr_s() {
  while (true) {
    auto p = token_i;
    auto ok = match({SEMI,LF}) and expr();
    if (not ok) {
      token_i = p;
      break;
    }
  }
  return true;
}

bool Parser::nve() {
  auto p = token_i;
  auto ok = noun() and verb() and expr();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::te() {
  auto p = token_i;
  auto ok = term() and expr();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::term() {
  auto p = token_i;
  auto ok = noun() or verb();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::noun() {// noun ::= term "[" Exprs "]" | "(" Exprs ")" | "{" Exprs "}" | Noun
  auto p = token_i;
  auto ok = Noun(); // term() and eat(LS) and exprs() and eat(RS);
  if (not ok) token_i = p;
  ok = eat(LPAR) and exprs() and eat(RPAR);
  if (not ok) token_i = p;
  ok = eat(LCURLY) and exprs() and eat(RCURLY);
  if (not ok) token_i = p;
  ok = term() and eat(LSQUARE) and exprs() and eat(RSQUARE); // Noun();
  if (not ok) token_i = p;
  return ok;
}

// Noun ::= Names | Ints | Floats | String | Symbols
bool Parser::Noun() {
  auto p = token_i;
  auto ok = names() or ints() or floats() or strings() or symbols();
  if (not ok) token_i = p;
  return ok;
}

// Names  ::=  Name ("." Name)*
bool Parser::names() {
  auto p = token_i;
  auto ok = eat(NAME) and name_s();
  if (not ok) token_i = p;
  return ok;
}

//Name ::= [A-Za-z][A-Za-z0-9]*  (already handled in lexer)
bool Parser::name_s() {
  while (true) {
    auto p = token_i;
    auto ok = eat(DOT) and eat(NAME);
    if (not ok) {
      token_i = p;
      break;
    }
  }
  return true;
}

// verb ::= term Adverb | Verb
bool Parser::verb() {
  auto p = token_i;
  auto ok = (term() and Adverb()) or Verb();
  if (not ok) token_i = p;
  return ok;
}

// Verb  ::= Verb1 ":"? | "0:" | "1:"
// Verb1 ::= [-:+*%!&|<>=~,^#_$?@.]
bool Parser::Verb() {
  auto p = token_i;
  auto ok = match({AMP, AT, BANG, CARET, COLON, COMMA, DOLLAR, DOT, EQUAL, HASH,
      HUH, LESS, MINUS, MORE, PERCENT, PLUS, STAR, TILDE, UNDERBAR, VERT,});
  if (ok) {
    int p1 = p;
    if (not eat(COLON)) token_i = p1;
  } else {
    ok = match({LINES,BYTES});
  }
  if (not ok) token_i = p;
  return ok;
}

// Adverb ::= ['\/] ":"?
bool Parser::Adverb() {
  auto p = token_i;
  auto ok = match({QUOTE,SLASH,BACKSLASH,EACHLEFT,EACHRIGHT,STENCIL});
  if (not ok) token_i = p;
  return ok;
}
