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

#define SYNTAX_ENUM(F)                                        \
  F(OK) F(UNK) F(ERR)                                         \
  F(LC) F(RC)                                                 \
  F(LP) F(RP)                                                 \
  F(LS) F(RS)                                                 \
  F(STRING) F(NAME) F(NUMBER) F(COMMENT) F(SYMBOL)            \
  F(IO) F(STENCIL) F(EACHLEFT) F(EACHRIGHT) F(LINES) F(BYTES) \
  F(ALPHA) F(AMP) F(AT) F(BACKSLASH) F(BACKTICK) F(BANG)      \
  F(CARET) F(COLON) F(COMMA) F(DASH) F(DIGIT) F(DOLLAR)       \
  F(DOT) F(DQUOTE) F(END) F(EQUAL) F(HASH) F(HUH)             \
  F(LESS) F(LF) F(MORE) F(PERCENT) F(PLUS) F(QUOTE)           \
  F(SEMI) F(SLASH) F(SPACE) F(STAR) F(TAB) F(TILDE)           \
  F(UNDERBAR) F(VERT)
#define MAKE_ENUM(v) v,
#define MAKE_REPR(v) #v,

class Runtime {
public:
  enum Syntax {SYNTAX_ENUM(MAKE_ENUM)};
  std::vector<std::string> SyntaxRepr{SYNTAX_ENUM(MAKE_REPR)};

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
  Syntax err = OK;
  int lineNum = 1;
  std::string line; //current line
  int stringStart = 0; //start of string within current line
  std::string currentString = ""; //(possibly multi-line) current string token
  std::stack<char> tokenStack; //for nested brackets
  std::vector<std::tuple<int,int,Syntax,std::string> > tokens; //line, column, type, value

  // methods
  bool read(std::string);
  bool parse();
  bool eval();
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
