#ifndef PARSER_H_
#define PARSER_H_
#include "tokenbase.hpp"
#include <algorithm> // std::find
#include <vector>
#include <stack>
class Parser : public TokenBase { //inherits TokenEnum,TokenRepr,Token
  std::string err;
  unsigned token_i;
  bool parse_stmt();
  bool parse_expr();
  bool parse_nve();
  bool parse_te();
  bool parse_term();
  bool parse_verb();
  bool parse_adverb();
  bool parse_noun();
  bool parse_Noun();
  bool parse_names();
  bool parse_name_tails();
  bool parse_floats();
  bool parse_ints();
  bool parse_strings();
  bool parse_symbols();
  bool match(std::initializer_list<TokenEnum>);
public:
  Parser();
  std::vector<Token> tokens;
  bool parse(std::vector<Token>);
  bool error(int linenum=-1,int pos=-1);
};
#endif // PARSER_H_
