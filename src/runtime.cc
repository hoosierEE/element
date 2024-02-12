#include "runtime.h"

constexpr bool isdigit(char c) {return '0'<=c and c<='9';}
constexpr bool isalpha(char c) {return ('a'<=c and c<='z') or ('A'<=c and c<='Z');}

void Runtime::read(std::string line) {
  this->line = line;
  auto &num = this->lineNum;
  auto &t = this->tokens;
  int sz = line.size();
  bool instring=false;
  int stringStart=sz;

  for (int i=0;i<sz;i++) {
    char c=line[i];

    if (c=='"' and not instring) { //start of string, discard opening quote
      instring=true;
      stringStart=i+1;
      continue;
    }

    if (instring) {
      if (c=='"' and line[i-1] != '\\') {
        instring=false;
        t.push_back(std::make_tuple(num,stringStart,STRING,line.substr(stringStart,i-stringStart)));
        i += 1; //drop end quote
      }
      continue;
    }

    // handle single chars
    if (alphabet.find(c) != std::string::npos) {
      t.push_back(std::make_tuple(num,i,syntaxMap.at(c),std::string(1,c)));
      continue;
    }

    // handle 2 character cases
    switch (c) {
    case ' ':
    case '\t':
      break;

    case '\'': // ' or ':
      if(line[i+1]==':') {
        t.push_back(std::make_tuple(num,i,STENCIL,"':"));
        i += 1;
      } else {t.push_back(std::make_tuple(num,i,QUOTE,"'"));}
      break;

    case '\\':
      if(line[i+1]==':') {
        t.push_back(std::make_tuple(num,i,EACHLEFT,"':"));
        i += 1;
      } else {t.push_back(std::make_tuple(num,i,BACKSLASH,"'"));}
      break;

    case '/': // slash is special
      if (sz==2 or i>1 and line[i-1]==' ') {i=sz-1; break;} // comment go till end of line
      if (line[i+1]==':') {t.push_back(std::make_tuple(num,i,EACHRIGHT,"/:")); i+=1; break;}
      else {t.push_back(std::make_tuple(num,i,SLASH,"/")); break;}

    default: // arbitrary-length tokens
      if (c=='0' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,LINES,"0:")); i+=1; break;}
      if (c=='1' and i+1<sz and line[i+1]==':') {t.push_back(std::make_tuple(num,i,BYTES,"1:")); i+=1; break;}
      if (isdigit(c)) {
        int numStart = i;
        while (i<sz and isdigit(c)) c=line[i++];
        if (c=='.' and i+1<sz and isdigit(line[i+1])) {
          i += 1; //pass dot
          c=line[i];
          while (i<sz and isdigit(c)) c=line[i++];
        }
        t.push_back(std::make_tuple(num,numStart,NUMBER,line.substr(numStart,i-numStart))); //implicit +1 for dot
        break;
      }

      if (isalpha(c)) {
        int nameStart = i;
        while (isalpha(c)) c=line[i++];
        t.push_back(std::make_tuple(num,nameStart,NAME,line.substr(nameStart,i-nameStart)));
        break;
      }
      this->err=UNK; error(); break;
    }
  }
  num += 1;
}

void Runtime::parse() {}
void Runtime::eval(){}

void Runtime::print(){
  // std::cout << "out[" << this->lineNum << "]: " << this->line << std::endl;
  std::cout << "[tokens]:" << std::endl;
  for (auto t : this->tokens) {
    int line,col;
    Syntax syn;
    std::string s;
    std::tie(line,col,syn,s) = t;
    std::cout << "line:" << line << " col:" << col << " syn:" << syn << " s:" << s << " " << std::endl;
  }
}

bool Runtime::error() {
  auto m = this->err;
  if (m==OK) return false;
  std::cerr << "ERROR (" << errmsg[m] << ") [line " << this->lineNum << "]" << std::endl;
  std::cerr << this->line << std::endl;
  this->err = OK; //reset
  return true;
}
