#ifndef PARSER_H_
#define PARSER_H_
#include "tokenbase.hpp"
#include <algorithm> // std::find
#include <vector>
#include <stack>
class Parser : public TokenBase { //inherits TokenEnum,TokenRepr,Token
  std::string err;
  unsigned token_i;
  bool exprs();   bool expr(); bool expr_s();
  bool nve();     bool te();   bool term();
  bool noun();    bool Noun();
  bool floats();  bool ints();
  bool names();   bool name_s();
  bool verb();    bool Verb(); bool Adverb();
  bool strings(); bool symbols();
  bool eat(TokenEnum);
  bool match(std::initializer_list<TokenEnum>);
public:
  Parser();
  std::vector<Token> tokens;
  bool parse(std::vector<Token>);
  bool error(int linenum=-1,int pos=-1);
};
#endif // PARSER_H_
