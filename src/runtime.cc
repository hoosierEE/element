#include "runtime.h"

void Runtime::read(std::string line) {
  this->line = line;
}

void Runtime::parse() {
}

void Runtime::eval(){
}

void Runtime::print(){
  std::cout << this->line << std::endl;
}

bool Runtime::error() {
  auto m = this->err;
  if (m != OK) {
    std::cerr << errmsg[m] << std::endl;
    this->err = OK; //reset
    return true;
  }
  return false;
}
