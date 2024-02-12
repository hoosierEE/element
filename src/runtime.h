#ifndef RUNTIME_H_
#define RUNTIME_H_

#include <iostream>
#include <map>
#include <vector>
#include <stack>

// ascii [32-127) (note space at start)
//  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
// wvqvvvvappvvvvavnnnnnnnnnnvpvvvvvnnnnnnnnnnnnnnnnnnnnnnnnnnpvpvvpnnnnnnnnnnnnnnnnnnnnnnnnnnpvpv
// w______________________________________________________________________________________________ whitespace
// __q____________________________________________________________________________________________ quote
// _______a_______________________________________________________________________________________ adverb
// ________________nnnnnnnnnn_______nnnnnnnnnnnnnnnnnnnnnnnnnn______nnnnnnnnnnnnnnnnnnnnnnnnnn____ noun
// ________pp_________________p_______________________________p_p__p__________________________p_p_ punctuation
// _v_vvvv___vvvvvv__________v_vvvvv___________________________v_vv____________________________v_v verb


class Runtime {
  // Compiler and interpreter internals:
  // Read and attempt to parse one line at a time, but some constructs
  // span multiple lines e.g:
  // {
  // ...
  // }

public:
  enum Syntax {
    OK,UNK,ERR, //error codes
    LC, RC, LP, RP, LS, RS, //brackets
    STRING, NAME, NUMBER, COMMENT, SYMBOL, IO, //arbitrary length tokens
    STENCIL, EACHLEFT, EACHRIGHT, LINES, BYTES, // //2-char tokens: ': \: /: 0: 1:

    // single-char tokens:
    ALPHA,     // [a-zA-Z]
    AMP,       // &
    AT,        // @
    BACKSLASH,
    BACKTICK,  // `
    BANG,      // !
    CARET,     // ^
    COLON,     // :
    COMMA,     // ,
    DASH,      // -
    DIGIT,     // [0-9]
    DOLLAR,    // $
    DOT,       // .
    DQUOTE,    // "
    END,       // end-of-file
    EQUAL,     // =
    HASH,      // #
    HUH,       // ?
    LESS,      // <
    LF,        // \n

    MORE,      // >
    PERCENT,   // %
    PLUS,      // +
    QUOTE,     // '
    SEMI,      // ;
    SLASH,     // /
    SPACE,     // ( )
    STAR,      // *
    TAB,       // \t
    TILDE,     // ~
    UNDERBAR,  // _
    VERT,      // |
  };

  const std::string alphabet = "~`!@#$%^&*()_-+={[]}|:;<,>.?"; //partial alphabet

  const std::map<char,Syntax> syntaxMap = {
    {'{',LC},{'}',RC},
    {'(',LP},{')',RP},
    {'[',LS},{']',RS},
    {'&',AMP},
    {'@',AT},
    {'\\',BACKSLASH},
    {'`',BACKTICK},
    {'!',BANG},
    {'^',CARET},
    {':',COLON},
    {',',COMMA},
    {'-',DASH},
    {'$',DOLLAR},
    {'.',DOT},
    {'"',DQUOTE},
    {'=',EQUAL},
    {'#',HASH},
    {'?',HUH},
    {'<',LESS},
    {'\n',LF},
    {'>',MORE},
    {'%',PERCENT},
    {'+',PLUS},
    {'\'',QUOTE},
    {';',SEMI},
    {'/',SLASH},
    {' ',SPACE},
    {'*',STAR},
    {'\t',TAB},
    {'~',TILDE},
    {'_',UNDERBAR},
    {'|',VERT},
  };

  std::string line; //current line
  int lineNum=1; //position in file or multi-line expr
  std::stack<Syntax> tokenStack; // {[()[]]{}[]}[] etc.
  std::vector<std::tuple<int,int,Syntax,std::string> > tokens; //line, column, type, value
  Syntax err = OK;

  // methods
  void read(std::string);
  void parse();
  void eval();
  void print();
  bool error();

  // error messages
  std::map<const Syntax,const std::string> errmsg{
    {ERR,"error"},
    {UNK,"unknown token"},
    {QUOTE,"unclosed quote"},
    {RC,"mismatched '}'"},
    {RP,"mismatched ')'"},
    {RS,"mismatched ']'"},
    {END,"unexpected end of file"}
  };
};

#endif // RUNTIME_H_
