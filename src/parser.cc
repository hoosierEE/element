#include "parser.hpp"
Parser::Parser() {}

bool Parser::error(int line, int pos) {return true;} // TODO

bool Parser::parse(std::vector<Token> ts) {
  this->tokens = ts;
  token_i = 0;
  return parse_exprs();
}

bool Parser::eat(TokenEnum t) {
  bool ok = token_i < tokens.size() and t == tokens[token_i].type;
  token_i += ok;
  return ok;
}

bool Parser::match(std::initializer_list<TokenEnum> ts) {
  bool ok = token_i < tokens.size() and std::find(ts.begin(),ts.end(),tokens[token_i].type) == ts.end();
  token_i += ok;
  return ok;
}

bool Parser::parse_exprs() {
  return parse_expr() and parse_expr_tails();
}

bool Parser::parse_expr_tails() {
  while (true) {
    auto p = token_i;
    auto ok = match({SEMI,LF}) and parse_expr();
    if (not ok) {token_i = p; break;}
  }
  return true;
}

bool Parser::parse_expr() {return parse_nve() or parse_te() or true;}

bool Parser::parse_nve() {
  auto p = token_i;
  auto ok = parse_noun() and parse_verb() and parse_expr();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_te() {
  auto p = token_i;
  auto ok = parse_term() and parse_expr();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_term() {
  auto p = token_i;
  auto ok = parse_noun() or parse_verb();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_noun() {
  // noun   ::=  term "[" Exprs "]" | "(" Exprs ")" | "{" Exprs "}" | Noun
  auto p = token_i;
  auto ok = parse_term() and eat(LS) and parse_exprs() and eat(RS);
  if (not ok) token_i = p;
  ok = eat(LP) and parse_exprs() and eat(RP);
  if (not ok) token_i = p;
  ok = eat(LC) and parse_exprs() and eat(RC);
  if (not ok) token_i = p;
  ok = parse_Noun();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_Noun() {
  // Noun   ::=  Names | Ints | Floats | String | Symbols
  auto p = token_i;
  auto ok = parse_names() or parse_ints() or parse_floats() or parse_strings() or parse_symbols();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_names() {
  // Names  ::=  Name ("." Name)*
  // Name   ::=  [A-Za-z][A-Za-z0-9]*
  auto p = token_i;
  auto ok = eat(NAME) and parse_name_tails();
  if (not ok) token_i = p;
  return ok;
}

bool Parser::parse_name_tails() {
  while (true) {
    auto p = token_i;
    auto ok = eat(DOT) and eat(NAME);
    if (not ok) {token_i = p; break;}
  }
  return true;
}

bool Parser::parse_verb() {
  // Verb   ::=  Verb1 ":"? | "0:" | "1:"
  // Verb1  ::=  [-:+*%!&|<>=~,^#_$?@.]
  auto p = token_i;
  auto ok = match(
    {DASH,COLON,PLUS,STAR,PERCENT,BANG,AMP,VERT,LESS,MORE,
     EQUAL,TILDE,COMMA,CARET,HASH,UNDERBAR,DOLLAR,HUH,AT,DOT});
  if (ok) {
    int p1 = p;
    if (not match({COLON})) token_i = p1;
  } else {
    ok = match({LINES,BYTES});
  }
  if (not ok) token_i = p;
  return ok;
}

// bool Parser::eval(){
//   if (tokenstack.empty() and not instring) {
//     // this->reset();
//   }
//   return false;
// }

// The "essence" of K's grammar:  E:E;e|e e:nve|te| t:n|v v:tA|V n:t[E]|(E)|{E}|N
// brief explanation: https://discord.com/channels/821509511977762827/821511172305846322/1107809632073826374
// Below is adapted from https://k.miraheze.org/wiki/Grammar
// Exprs  ::=  expr (";" expr)*
// expr   ::=  noun verb expr | term expr | ε
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
