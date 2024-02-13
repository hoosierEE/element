#include "runtime.h"

constexpr bool isdigit(char c) {return '0'<=c and c<='9';}
constexpr bool isalpha(char c) {return ('a'<=c and c<='z') or ('A'<=c and c<='Z');}

/// return true if error
bool Runtime::read(std::string line) {
  this->line = line;
  auto &num = this->lineNum;
  auto &t = this->tokens;
  auto &s = this->tokenStack;
  int sz = line.size();
  bool instring = false;

  for (int i=0;i<sz;i++) {
    char c=line[i];

    // continue processing a string
    if (instring) {
      int pos = line.substr(i).find('"');
      if (pos != std::string::npos and this->currentString.back() != '\\') {//found closing quote
        t.push_back(std::make_tuple(num,i,STRING,this->currentString + line.substr(i,pos+1-i)));
        this->currentString = ""; instring = false; //reset
        i = pos+1; //jump forward past quote
      } else {
        this->currentString += std::string(1,c); // otherwise append current char
      }
      continue;
    }

    switch (c) {
    case ' ': case '\t': break; // whitespace
    case '"': this->stringStart = i; instring = true; break; //begin string
    case '(': case '[': case '{': //stack ops
      t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
      s.push(c); break;
    case '}':
      if (s.empty() or s.top()!='{') {this->err = RC; return true;}
      t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
      s.pop(); break;
    case ']':
      if (s.empty() or s.top()!='[') {this->err = RS; return true;}
      t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
      s.pop(); break;
    case ')':
      if (s.empty() or s.top()!='(') {this->err = RP; return true;}
      t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
      s.pop(); break;

    // handle 2 character tokens except slash
    case '\'': // eachprior or each
      if (line[i+1]==':') {t.push_back(std::make_tuple(num,i,STENCIL,"':")); i++;}
      else {t.push_back(std::make_tuple(num,i,QUOTE,"'"));} break;

    case '\\': // eachleft or backslash
      if(line[i+1]==':') {t.push_back(std::make_tuple(num,i,EACHLEFT,"\\:")); i++;}
      else {t.push_back(std::make_tuple(num,i,BACKSLASH,"\\"));} break;

    case '/': // slash is special
      if (sz==1 or i>1 and line[i-1]==' ') {i=sz-1; break;} // comment continues till end of line
      if (line[i+1]==':') {t.push_back(std::make_tuple(num,i,EACHRIGHT,"/:")); i++; break;}
      else {t.push_back(std::make_tuple(num,i,SLASH,"/")); break;}

    default: // arbitrary-length tokens
      if (c=='0' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,LINES,"0:")); i++; break;}
      if (c=='1' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,BYTES,"1:")); i++; break;}

      // number
      if (isdigit(c)) {
        int numStart = i;         while (i<sz and isdigit(line[i+1])) i++;
        if (line[i+1]=='.') {i++; while (i<sz and isdigit(line[i+1])) i++;}
        t.push_back(std::make_tuple(num,numStart,NUMBER,line.substr(numStart,i-numStart+1)));
        break;
      }

      // identifiers
      if (isalpha(c)) {
        int nameStart = i; while (i<sz and isalpha(line[i+1])) i++;
        t.push_back(std::make_tuple(num,nameStart,NAME,line.substr(nameStart,i-nameStart+1)));
        break;
      }

      // statement separator
      if (c=='\n' and s.empty()) {t.push_back(std::make_tuple(num,i,SEMI,";")); break;}

      // handle remaining 1-char tokens
      if (syntaxMap.count(c)) { // alphabet.find(c) != std::string::npos) {
        t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
        continue;
      }

      this->err=UNK; error(); break;
    }
  }
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
  std::cerr << "[ERROR] " << errmsg[m] << " [" << this->lineNum << "]" << std::endl;
  std::cerr << this->line << std::endl;
  this->err = OK; //reset
  return true;
}
