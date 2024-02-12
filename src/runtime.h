#ifndef RUNTIME_H_
#define RUNTIME_H_

#include <iostream>
#include <map>
#include <vector>
#include <stack>

class Runtime {
  // Compiler and interpreter internals:
  // Read and attempt to parse one line at a time, but some constructs
  // span multiple lines e.g:
  // {
  // ...
  // }
public:
  enum Syntax {
    OK,ERR, //error codes
    LC, RC, LP, RP, LS, RS, //brackets
    STRING, NAME, NUMBER, COMMENT, SYMBOL, ADVERB, IO, //multi-char tokens
    // single-char tokens:
    ALPHA,     // [a-zA-Z]
    AMP,       // &
    AT,        // @
    BACKSLASH, // \\
    BACKT,     // `
    BANG,      // !
    CARET,     // ^
    COLON,     // :
    COMMA,     // ,
    DASH,      // -
    DIGIT,     // [0-9]
    DOLLAR,    // $
    DOT,       // .
    DQUOTE,    // "
    EQUAL,     // =
    HASH,      // #
    HUH,       // ?
    LESS,      // <
    MORE,      // >
    PERCENT,   // %
    PLUS,      // +
    QUOTE,     // '
    SEMI,      // ;
    SLASH,     // /
    SPACE,     // ( )
    STAR,      // *
    TILDE,     // ~
    UNDER,     // _
    VERT,      // |
    END        //end-of-file
  };
  std::string line; //current line
  int lineNum=0; //position in file or multi-line expr
  std::stack<Syntax> tokenStack;
  std::vector<std::string> tokens;
  Syntax err = OK;

  void read(std::string);
  void parse();
  void eval();
  void print();

  bool error();

  // some error messages
  std::map<const Syntax,const std::string> errmsg{
    {ERR,"error"},
    {QUOTE,"unclosed quote"},
    {RC,"mismatched '}'"},
    {RP,"mismatched ')'"},
    {RS,"mismatched ']'"},
    {END,"unexpected end of file"}
  };
};

#endif // RUNTIME_H_
