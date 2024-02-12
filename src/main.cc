#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h"

#include "nicerepl.h" //install_handler, global_status_flag
#include "runtime.h" //Runtime
#include <iostream>
#include <filesystem>
#include <fstream>


int main(int argc, char *argv[]) {

  // handle --help -h for application before passing remaining args to doctest
  for (int i=1; i < argc; i++) {
    auto arg = std::string(argv[i]);
    if (arg == "-h" or arg == "--help") {
      std::cout << "help message" << std::endl;
      return 0;
    }
  }

  install_handler(); //Ctrl+C handling

  // automatically run tests at runtime
  // a.out inherits all the options of doctest

  doctest::Context context;
  context.setOption("minimal", true);
  context.applyCommandLine(argc,argv);
  int res = context.run();
  if (context.shouldExit()) {return res;}

  if (argc > 3) {
    std::cerr << "unknown arguments" << std::endl;
    // https://man.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+4.3-RELEASE&format=html
    return 64; // EX_USAGE: "The command was used incorrectly"
  }

  Runtime runtime;

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

      // display error but don't crash. reset error each loop.
      runtime.error();

      runtime.read(line);
      runtime.parse();
      runtime.eval();
      runtime.print();
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
          // Don't continue if we previously detected an error
          // EX_DATAERR is a generic "user data" error code
          if (runtime.error()) {return 65;}
          runtime.read(line);
          runtime.parse();
          runtime.eval();
          runtime.print();
        }
      } else {
        std::cerr << "unable to open file" << std::endl;
        return 66; // EX_NOINPUT "An input file did not exist or was not readable"
      }
    }
  }

  // string
  if (argc == 3 and std::string(argv[1]) == "--eval") {// ./a.out --eval "2+3"
    runtime.read(std::string(argv[2]));
    runtime.parse();
    runtime.eval();
    runtime.print();
  }

  return 0;
}

TEST_CASE("runtime class") {
  Runtime runtime;
  runtime.read(std::string("hello"));
  CHECK(runtime.line.size() == 5);
}
