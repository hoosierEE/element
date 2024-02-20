#ifndef PARSER_H_
#define PARSER_H_
#include "tokenbase.hpp"
#include <algorithm> // std::find
#include <vector>
#include <stack>
// #define TOKEN_ENUM(F) F(ALPHA) F(AMP) F(AT) F(BACKSLASH) F(BACKTICK) F(BANG) \
//   F(BYTES) F(CARET) F(COLON) F(COMMA) F(COMMENT) F(DASH) F(DIGIT) F(DOLLAR) F(DOT) \
//   F(DQUOTE) F(EACHLEFT) F(EACHRIGHT) F(EQUAL) F(HASH) F(HUH) \
//   F(LC) F(LESS) F(LF) F(LINES) F(LP) F(LS) F(MORE) F(NAME) F(NUMBER) F(PERCENT) \
//   F(PLUS) F(QUOTE) F(RC) F(RP) F(RS) F(SEMI) F(SEP) F(SLASH) F(SPACE) F(STAR) \
//   F(STENCIL) F(STRING) F(SYMBOL) F(TAB) F(TILDE) F(UNDERBAR) F(UNK) F(VERT) F(OK)
class Parser : public TokenBase { //inherits TokenEnum,TokenRepr,Token
public:
  Parser();
  std::vector<TokenBase::Token> tokens;
  void parse(std::vector<TokenBase::Token>);
  int token_i;
  std::string err;
  bool error(int linenum=-1,int pos=-1);
  bool parse_stmt();
  bool parse_expr();
  bool match(std::initializer_list<TokenBase::Token>);
};
#endif // PARSER_H_
