#ifndef TOKEN_BASE_H_
#define TOKEN_BASE_H_
#include <vector>
#include <string>
#define MAKE_ENUM(v) v,
#define MAKE_REPR(v) #v,
#define TOKEN_ENUM(F) F(ALPHA) F(AMP) F(AT) F(BACKSLASH) F(BACKTICK) F(BANG) \
  F(BYTES) F(CARET) F(COLON) F(COMMA) F(COMMENT) F(MINUS) F(DIGIT) F(DOLLAR) F(DOT) \
  F(DQUOTE) F(EACHLEFT) F(EACHRIGHT) F(EQUAL) F(HASH) F(HUH) \
  F(LCURLY) F(LESS) F(LF) F(LINES) F(LPAR) F(LSQUARE) F(MORE) F(NAME) F(NUMBER) F(PERCENT) \
  F(PLUS) F(QUOTE) F(RCURLY) F(RPAR) F(RSQUARE) F(SEMI) F(SEP) F(SLASH) F(SPACE) F(STAR) \
  F(STENCIL) F(STRING) F(SYMBOL) F(TAB) F(TILDE) F(UNDERBAR) F(UNK) F(VERT) F(OK)

struct TokenBase {
  enum TokenEnum{TOKEN_ENUM(MAKE_ENUM)};
  const std::vector<std::string> TokenRepr{TOKEN_ENUM(MAKE_REPR)};
  struct Token {int line, pos; std::string s; TokenEnum type;};
};
#endif // TOKEN_BASE_H_
