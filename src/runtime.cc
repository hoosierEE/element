#include "runtime.h"
#define addtoken(c) t.push_back(std::make_tuple(num,i,syntaxmap.at(c),std::string(1,c)))
constexpr bool isdigit(char c) {return '0'<=c and c<='9';}
constexpr bool isalpha(char c) {return ('a'<=c and c<='z') or ('A'<=c and c<='Z');}
bool Runtime::read(std::string line) {//return true if error
  this->line = line;
  auto &num = this->linenum;
  auto &t = this->tokens;
  auto &s = this->tokenstack;
  auto &st = this->instring;
  auto &cs = this->currentstring;
  int i;
  int sz = line.size();
  for (i=0;i<sz;i++) {
    char c=line[i];
    // continue processing a string
    if (st) {
      if (c=='"') {
        if (cs.back()=='\\') {cs[cs.size()-1] = '"';}
        else {t.push_back(std::make_tuple(num,i,STRING,cs)); st=false; cs="";}
      }
      else {cs += std::string(1,c);}
      continue;
    }

    switch (c) {
    case' ':case'\t':break; // whitespace
    case'"':st=true;break; //begin string
    case'(':case'[':case'{':addtoken(c);s.push(c);break; //stack ops
    case'}':if(s.empty()or s.top()!='{'){this->err=RC;return true;}addtoken(c);s.pop();break;
    case']':if(s.empty()or s.top()!='['){this->err=RS;return true;}addtoken(c);s.pop();break;
    case')':if(s.empty()or s.top()!='('){this->err=RP;return true;}addtoken(c);s.pop();break;

    // handle 2 character tokens except slash
    case '\'': // eachprior or each
      if (line[i+1]==':') {t.push_back(std::make_tuple(num,i,STENCIL,"':")); i++;}
      else {t.push_back(std::make_tuple(num,i,syntaxmap.at(c),"'"));} break;

    case '\\': // eachleft or backslash
      if(line[i+1]==':') {t.push_back(std::make_tuple(num,i,EACHLEFT,"\\:")); i++;}
      else {t.push_back(std::make_tuple(num,i,syntaxmap.at(c),"\\"));} break;

    case '/': // slash is special
      if (sz==1 or i>1 and line[i-1]==' ') {i=sz-1; break;} // comment continues till end of line
      if (line[i+1]==':') {t.push_back(std::make_tuple(num,i,EACHRIGHT,"/:")); i++; break;}
      else {t.push_back(std::make_tuple(num,i,SLASH,"/")); break;}

    default: // arbitrary-length tokens
      if (c=='0' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,LINES,"0:")); i++; break;}
      if (c=='1' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,BYTES,"1:")); i++; break;}
      if (isdigit(c)) {// number
        int start = i;            while (i<sz and isdigit(line[i+1])) i++;
        if (line[i+1]=='.') {i++; while (i<sz and isdigit(line[i+1])) i++;}
        t.push_back(std::make_tuple(num,start,NUMBER,line.substr(start,i-start+1))); break;
      }
      if (isalpha(c)) {// identifiers
        int start = i;            while (i<sz and isalpha(line[i+1])) i++;
        t.push_back(std::make_tuple(num,start,NAME,line.substr(start,i-start+1))); break;
      }
      if (syntaxmap.count(c)) {addtoken(c); break;} //other 1-char tokens
      this->err=UNK; error(); break; //how did you even type that?
    }
  }

  if (st) {cs += "\n";}
  else {t.push_back(std::make_tuple(num,i,SEP,""));}
  num++;
  return false;
}

bool Runtime::parse() {return false;}
bool Runtime::eval(){return false;}

void Runtime::print(){
  std::cout << "[tokens]:" << std::endl;;
  for (auto &t : this->tokens) {
    std::cout << SyntaxRepr[std::get<2>(t)] << "\t" << std::get<3>(t) << std::endl;
  }
}

bool Runtime::error() {
  auto m = this->err;
  if (m==OK) return false;
  std::cerr << "[ERROR] " << errmsg[m] << " [" << this->linenum << "]" << std::endl;
  std::cerr << this->line << std::endl;
  this->err = OK; //reset
  return true;
}
