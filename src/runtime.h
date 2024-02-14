#ifndef RUNTIME_H_
#define RUNTIME_H_
#include <iostream>
#include <map>
#include <vector>
#include <stack>
#define MAKE_ENUM(v) v,
#define MAKE_REPR(v) #v,
#define SYNTAX_ENUM(F) F(ALPHA) F(AMP) F(AT) F(BACKSLASH) F(BACKTICK) F(BANG) F(BYTES) F(CARET) F(COLON) F(COMMA) F(COMMENT) F(DASH) F(DIGIT) F(DOLLAR) F(DOT) F(DQUOTE) F(EACHLEFT) F(EACHRIGHT) F(END) F(EQUAL) F(ERR) F(HASH) F(HUH) F(IO) F(LC) F(LESS) F(LF) F(LINES) F(LP) F(LS) F(MORE) F(NAME) F(NUMBER) F(OK) F(PERCENT) F(PLUS) F(QUOTE) F(RC) F(RP) F(RS) F(SEMI) F(SEP) F(SLASH) F(SPACE) F(STAR) F(STENCIL) F(STRING) F(SYMBOL) F(TAB) F(TILDE) F(UNDERBAR) F(UNK) F(VERT)

class Runtime {
public:
  enum Syntax {SYNTAX_ENUM(MAKE_ENUM)};
  std::vector<std::string> SyntaxRepr{SYNTAX_ENUM(MAKE_REPR)};
  const std::string alphabet = "~`!@#$%^&*()_-+={[]}|:;<,>.?"; //partial alphabet
  const std::map<char,Syntax> syntaxmap = {
    {'{',LC},{'}',RC},{'(',LP},{')',RP},{'[',LS},{']',RS},
    {'&',AMP},{'@',AT},{'\\',BACKSLASH},{'`',BACKTICK},{'!',BANG},
    {'^',CARET},{':',COLON},{',',COMMA},{'-',DASH},{'$',DOLLAR},
    {'.',DOT},{'"',DQUOTE},{'=',EQUAL},{'#',HASH},{'?',HUH},
    {'<',LESS},{'\n',LF},{'>',MORE},{'%',PERCENT},{'+',PLUS},
    {'\'',QUOTE},{';',SEMI},{'/',SLASH},{' ',SPACE},{'*',STAR},
    {'\t',TAB},{'~',TILDE},{'_',UNDERBAR},{'|',VERT},
  };

  std::map<const Syntax,const std::string> errmsg{
    {ERR,"error"},
    {UNK,"unknown token"},
    {QUOTE,"unclosed quote"},
    {RC,"mismatched '}'"},
    {RP,"mismatched ')'"},
    {RS,"mismatched ']'"},
    {END,"unexpected end of file"}
  };
  Syntax err = OK;
  int linenum = 1;
  int stringstart = 0; //start of string within current line
  bool instring=false;
  std::string currentstring = ""; //(possibly multi-line) current string token

  std::string line; //current line
  std::stack<char> tokenstack; //for nested brackets
  std::vector<std::tuple<int,int,Syntax,std::string> > tokens; //line, column, type, value

  // methods
  bool read(std::string);
  bool parse();
  bool eval();
  void print();
  bool error();

};

#endif // RUNTIME_H_
