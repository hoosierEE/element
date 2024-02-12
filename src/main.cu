// Perhaps a crazy idea.
// Compiler and interpreter for a K dialect, implemented in cuda C++.
//
// compile:
//   $ nvcc main.cu
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
  OK,
  ERR_UNBAL, // unbalanced parentheses
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
  Err syntaxErr=OK;
  Err parseErr=OK;
  std::map<Err,std::string> msyntax{
    {OK,""},
    {ERR_UNBAL,"unbalanced parentheses"}
  };
  std::map<Err,std::string> mparse{
    {OK,""}
  };
  std::stack<char> bracket_stack;
  std::string line;
  std::vector<Code> tokens;
  Err read(std::string);
  Err eval();
  void print();
  void repl(std::string);
  void pbal(Err*,char);
};


void Repl::repl(std::string line) {
  Err e{OK};
  if ((e=read(line)) != OK) std::cout << "`syntax\n" << msyntax[e] << std::endl;
  if ((e=eval())     != OK) std::cout <<  "`parse\n" <<  mparse[e] << std::endl;
  print();
}


bool Repl::pbal(Err *e, char c) {
  // set Repl error code if paren is not balanced
  auto& s = this->bracket_stack;
  if(s.empty() || s.top()!=c) {
    *e = OK;
    this->syntaxErr = ERR_UNBAL;
    return false;
  }
  s.pop();
  return s.empty();
}


Err Repl::read(std::string line) {
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
  return e;
}


Err Repl::eval(){return OK;}
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

  // string
  if (argc == 2) repl.repl(std::string(argv[1]));
}