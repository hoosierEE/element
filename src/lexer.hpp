#ifndef LEXER_H_
#define LEXER_H_
#include "tokenbase.hpp"
#include <iostream>
#include <map>
#include <vector>
class Lexer : public TokenBase { //inherits TokenEnum, TokenRepr, Token
public:
  const std::map<char,TokenEnum> syntaxmap={
    {'{',LC},{'}',RC},{'(',LP},{')',RP},{'[',LS},{']',RS},
    {'&',AMP},{'@',AT},{'\\',BACKSLASH},{'`',BACKTICK},{'!',BANG},
    {'^',CARET},{':',COLON},{',',COMMA},{'-',DASH},{'$',DOLLAR},
    {'.',DOT},{'"',DQUOTE},{'=',EQUAL},{'#',HASH},{'?',HUH},
    {'<',LESS},{'\n',LF},{'>',MORE},{'%',PERCENT},{'+',PLUS},
    {'\'',QUOTE},{';',SEMI},{'/',SLASH},{' ',SPACE},{'*',STAR},
    {'\t',TAB},{'~',TILDE},{'_',UNDERBAR},{'|',VERT}
  };

  // mutable
  bool instring;
  int linenum;
  std::string currentstring; //(possibly multi-line) current string token
  std::string line; //current line
  std::vector<Token> tokens; //line, column, type, value

  Lexer();
  void lex(std::string); //returns error message
  std::string err;
  bool error(int linenum=-1,int pos=-1);
};
#endif // LEXER_H_
