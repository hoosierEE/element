#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h" //https://github.com/doctest/doctest
#include "lexer.hpp"
#include "parser.hpp"
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iostream>

// https://man.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+4.3-RELEASE&format=html
#define EX_USAGE   64 //The command was used incorrectly
#define EX_DATAERR 65 //The input data was incorrect in some way.
#define EX_NOINPUT 66 //An input file did not exist or was not readable.
#define EX_IOERR   74 //An error occurred while doing I/O on some file.
#define EX_NOHOST  68 //The host specified did not exist.

// credit goes to: https://gist.github.com/clwyatt/58169c7b0053c49cc36cca67f4c77cdc
volatile sig_atomic_t global_status_flag = 0;
// this function is called when a signal is sent to the process
void interrupt_handler(int signal_num) {
  if(signal_num == SIGINT) { //handle Ctrl+C
    //simulate sending EOF to std::getline
    std::cin.setstate(std::ios::eofbit);
    // if not reset since last call, exit
    if (global_status_flag > 0) exit(EXIT_FAILURE);
    ++global_status_flag;
  }
}
// install the signal handler
inline void install_handler() {
  struct sigaction sigIntHandler;
  sigIntHandler.sa_handler = interrupt_handler;
  sigemptyset(&sigIntHandler.sa_mask);
  sigIntHandler.sa_flags = 0;
  sigaction(SIGINT, &sigIntHandler, NULL);
}

int main(int argc, char *argv[]) {
  // handle --help or -h before passing remaining args to doctest. TODO: pass *no* args to doctest?
  for (int i=1; i < argc; i++) {
    auto arg = std::string(argv[i]);
    if (arg == "-h" or arg == "--help") {
      std::cout << "Element version 0" << std::endl;
      std::cout << "usage:" << std::endl;
      std::cout << argv[0] << " --help    # (or -h) print this message" << std::endl;
      std::cout << argv[0] << "           # interactive REPL" << std::endl;
      std::cout << argv[0] << " filename  # run a script file" << std::endl;
      return 0;
    }
  }

  install_handler(); //handle ^C

  // automatically run tests at runtime
  // a.out inherits all doctest options
  doctest::Context context;
  context.setOption("minimal", true);
  context.applyCommandLine(argc,argv);
  int res = context.run();
  if (context.shouldExit()) {return res;}

  Lexer lexer;
  Parser parser;

  // repl (or stdin)
  if (argc == 1) {
    while (true) {
      global_status_flag = 0; //reset
      std::cout << "lmnt> ";
      std::string line;
      std::getline(std::cin, line);
      // handle Ctrl+C
      if (std::cin.fail() and global_status_flag > 0) {
        std::cin.clear(); //reset eof state
        std::cout << std::endl;
        continue;
      }
      if (std::cin.eof()) {break;} // handle Ctrl+D
      // display any errors but don't crash - just reset error each loop
      lexer.lex(line); if (lexer.error()) continue;
      parser.parse(lexer.tokens); if (parser.error()) continue;
      std::cout << "[tokens]:" << std::endl;;
      for (auto &t : parser.tokens) {
        std::cout << parser.TokenRepr[t.type] << "\t" << t.s << std::endl;
      }

      // lexer.parse();   if (lexer.error()) continue;
      // lexer.eval();    if (lexer.error()) continue;
      // lexer.print();
    }
  }

  // file
  if (argc == 2) {// assume argv[1] is a path. compile and run each line
    std::filesystem::path p(argv[1]);
    if (std::filesystem::exists(p) and std::filesystem::is_regular_file(p)) {
      std::ifstream file(argv[1]);
      if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
          // Crash on error
          lexer.lex(line); if (lexer.error()) return EX_DATAERR;
          parser.parse(lexer.tokens); if (parser.error()) return EX_DATAERR;
          // lexer.eval();    if (lexer.error()) return EX_DATAERR;
          // lexer.print();
        }
        // lexer.tokens.push_back({lexer.linenum,0,Lexer::END,""});
      } else {
        std::cerr << "unable to open file" << std::endl;
        return EX_NOINPUT;
      }
    }
  }

  return 0;
}

// tests
TEST_CASE("runtime class") {
  Lexer lexer;
  lexer.lex(std::string("x:3"));
  // for (auto &t: lexer.tokens)
  //   std::cout << t.s <<" "<< lexer.TokenRepr[t.type] << std::endl;
  CHECK(lexer.tokens.size() == 4);
  CHECK(lexer.error() == false);
  Parser parser;
  parser.parse(lexer.tokens);
  // CHECK(parser.token_i == 4);
  CHECK(lexer.tokens[0].type == Lexer::NAME);
}
