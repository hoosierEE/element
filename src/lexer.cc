#include "lexer.hpp"
#define addtoken(c) t.push_back({num,i,std::string(1,c),syntaxmap.at(c)})
constexpr bool isdigit(char c){return'0'<=c and c<='9';}
constexpr bool isalpha(char c){return('a'<=c and c<='z')or('A'<=c and c<='Z');}

Lexer::Lexer() {
  currentstring="";
  err="";
  instring=false;
  line="";
  linenum=1;
  tokens=std::vector<Token>();
}

/// Classify groups of characters as tokens.
/// Errors are malformed numbers (like "1.a" or "1a") or unknown characters.
void Lexer::lex(std::string line) {
  this->line = line;
  auto &num = linenum;
  auto &t   = tokens;
  auto &st  = instring;
  auto &cs  = currentstring;
  int sz = line.size();
  int i;
  for (i=0;i<sz;i++) {
    char c=line[i];
    // We need to check this before going into the switch(c) below, because
    // strings can contain the begin-comment character, spaces, etc. This "state
    // machine" kind of approach is required here because when we're operating
    // as a REPL, we can't know where the string ends until the user finishes
    // typing.
    if (st) { //we're in the middle of a string
      if (c=='"') { //ah, could this be the end of the string?
        if (cs.back()=='\\') {cs[cs.size()-1]='"';} // nope. a literal double-quote char
        else {t.push_back({num,i,cs,STRING}); st=false; cs="";} // yup. reset
      }
      else {cs += std::string(1,c);}
      continue;
    }

    switch (c) {
    case' ':case'\t':break; // whitespace
    case'"':st=true;break; //begin string

    // handle 2 character tokens except slash
    case '\'': // eachprior or each
      if (line[i+1]==':') {t.push_back({num,i,"':",STENCIL}); i++;}
      else {t.push_back({num,i,"'",syntaxmap.at(c)});} break;

    case '\\': // eachleft or backslash
      if(line[i+1]==':') {t.push_back({num,i,"\\:",EACHLEFT}); i++;}
      else {t.push_back({num,i,"\\",syntaxmap.at(c)});} break;

    case '/': // comment, eachright, or just slash
      if (sz==1 or (i>1 and line[i-1]==' ')) {i=sz-1; break;} // (comment) till eol
      if (line[i+1]==':') {t.push_back({num,i,"/:",EACHRIGHT}); i++; break;}
      else {t.push_back({num,i,"/",SLASH}); break;}

    default: // arbitrary-length tokens
      if (c=='0' and i+1<sz and line[i+1]==':') {t.push_back({num,i,"0:",LINES}); i++; break;}
      if (c=='1' and i+1<sz and line[i+1]==':') {t.push_back({num,i,"1:",BYTES}); i++; break;}
      if (isdigit(c)) {// number
        int start = i;            while (i<sz and isdigit(line[i+1])) i++;
        if (line[i+1]=='.') {
          if (not isdigit(line[i+2])) {err="malformed number"; error(num,i+2); break;}
          i++; /* consume dot */  while (i<sz and isdigit(line[i+1])) i++;
        }
        if (isalpha(line[i+1])) {err="malformed number"; error(num,i+1); break;}
        t.push_back({num,start,line.substr(start,i-start+1),NUMBER}); break;
      }
      if (isalpha(c)) {// identifiers
        int start = i;            while (i<sz and isalpha(line[i+1])) i++;
        t.push_back({num,start,line.substr(start,i-start+1),NAME}); break;
      }
      if (syntaxmap.count(c)) {addtoken(c); break;} //other 1-char tokens
      err="unknown token"; error(num,i); break; //how did you even type that?
    }
  }

  // end of std::getline
  if (st) {cs += "\n";}
  else {t.push_back({num,i,"\n",LF});}
  num++;
}

bool Lexer::error(int linenum, int pos) {
  auto m = err;
  if (m=="") return false; //no errors, yay
  std::cerr << "[SYNTAX (" << m << ") on line " << linenum << "]:" << std::endl;
  std::cerr << line << std::endl;
  std::cerr << std::string(pos,' ')+"^" << std::endl;
  err = ""; //reset
  return true;
}
