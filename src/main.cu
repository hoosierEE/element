// Perhaps a crazy idea.
// Compiler and interpreter for a K dialect, implemented in cuda C++.
//
// limitations:
//   line length must be < 256
//
// compile:
//   $ nvcc scanner.cu
//
// run a script file:
//   $ ./a.out < filename.ext
//
// eval a string:
//   $ ./a.out "a:7; a*2+3"  # prints 35
//
// start interactive interpreter:
//   $ ./a.out  # start interpreter
#include <iostream>
#include <map>
#include <stack>
#include <vector>

// ascii [32-127) (note space at start)
//  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
// wvqvvvvappvvvvavnnnnnnnnnnvpvvvvvnnnnnnnnnnnnnnnnnnnnnnnnnnpvpvvpnnnnnnnnnnnnnnnnnnnnnnnnnnpvpv
// w______________________________________________________________________________________________ whitespace
// __q____________________________________________________________________________________________ quote
// _______a_______________________________________________________________________________________ adverb
// ________________nnnnnnnnnn_______nnnnnnnnnnnnnnnnnnnnnnnnnn______nnnnnnnnnnnnnnnnnnnnnnnnnn____ noun
// ________pp_________________p_______________________________p_p__p__________________________p_p_ punctuation
// _v_vvvv___vvvvvv__________v_vvvvv___________________________v_vv____________________________v_v verb

enum Err {
  OK,ERR_UNBAL, //syntax errors
};

enum Code {
  END, //end of line
  COMMENT,QUOTE,SPACE,STR,ADVERB,ALPHA,NUMBER,SYMBOL, //syntax classes
  LP,RP,LS,RS,LC,RC,COLON,DOT,SEM,VERB, //more syntax classes
  UNK //unknown, catch-all
};

class Repl {
public:
  bool quote=false;
  Code syntaxErr=OK;
  Code parseErr=OK;
  std::map<Code,std::string> msyntax{
    {OK,""},
    {ERR_UNBAL,"unbalanced parentheses"}
  };
  std::map<Code,std::string> mparse{
    {OK,""}
  };
  std::stack<char> bracket_stack;
  std::string line;
  std::vector<Code> tokens;
  void read(std::string);
  void eval();
  void print();
  void repl(std::string);
  void pbal(char);
};


void Repl::repl(std::string line) {
  read(line);
  if (this->syntaxErr != OK) {
    std::cout << "`" << msyntax[this->syntaxErr] << std::endl;
  }
  eval();
  if (this->parseErr != OK) {
    std::cout << "`" << mparse[this->parseErr] << std::endl;
  }
  print();
}


void Repl::pbal(Err *e, char c) {
  // set Repl error code if paren is not balanced
  auto& s = this->bracket_stack;
  if(s.empty() || s.top()!=c) {
    *e = OK;
    this->syntaxErr = ERR_UNBAL;
  }
  s.pop();
}


void Repl::read(std::string line) {
  Err e = OK;
  this->line = line; //make a copy of the original
  int sz = line.size();
  bool comment=false;

  //aliases
  auto& q = this->quote;
  auto& s = this->bracket_stack;
  auto& t = this->tokens;

  for (int i=0;i<sz;i++) {
    char c = line[i];
    char d = c|' '; //uppercase temp variable
    if (comment) {t.push_back(COMMENT); continue;} //continue comment until eol
    if (q and c!='"') {t.push_back(STR);} //continue string until closing quote
    else if (c=='"') {
      if (q and line[i-1]!='\\') {q=false;}
      else {q=true; t.push_back(QUOTE);}
    }
    else if (c==' ' or c=='\t') {t.push_back(SPACE);}
    else if (c=='\'') t.push_back(ADVERB);
    else if (d>='a' and d<='z') t.push_back(ALPHA);
    else if (c>='0' and c<='9') t.push_back(NUMBER);
    else if (c=='/') {
      if (i==0 or tokens.back()==SPACE) {comment=true;t.push_back(COMMENT);}
      else {t.push_back(VERB);}
    }
    else if (c=='`') {t.push_back(SYMBOL);}
    else if (c=='(') {t.push_back(LP);s.push(c);}
    else if (c==')') {t.push_back(RP);pbal(&e,'(');}
    else if (c=='[') {t.push_back(LS);s.push(c);}
    else if (c==']') {t.push_back(RS);pbal(&e,'[');}
    else if (c=='{') {t.push_back(LC);s.push(c);}
    else if (c=='}') {t.push_back(RC);pbal(&e,'{');}
    else if (c==':') {t.push_back(COLON);}
    else if (c=='.') {t.push_back(DOT);}
    else if (c==';') {t.push_back(SEM);}
    else if (c>32 and c<127) {t.push_back(VERB);}
    else {t.push_back(UNK);}
  }
  t[line.size()]=END;
}


void Repl::eval(){}
void Repl::print(){
  for (auto &x : this->tokens) {
    std::cout << x << " ";
  }
  std::cout << std::endl;
}


int main(int argc, char*argv[]) {
  auto repl = Repl();
  // repl or stdin
  if (argc == 1)
    for (std::string line; std::getline(std::cin, line);)
      repl.repl(line);

  // string eval
  if (argc == 2)
    repl.repl(std::string(argv[1]));
}
