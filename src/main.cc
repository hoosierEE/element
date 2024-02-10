#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h"

#include "nicerepl.h" //install_handler, global_status_flag
// #include "scanner.h"
// #include <csignal>
#include <iostream>
// #include <string>


void run(std::string line) {
  Scanner scanner(line);
  std::vector<std::string> tokens(scanner.scanTokens());
  for (auto &t : tokens) {
    std::cout << t << std::endl;
  }
}


int main(int argc, char *argv[]) {
  install_handler(); //Ctrl+C handling

  doctest::Context context;
  context.setOption("minimal", true);
  context.applyCommandLine(argc,argv);
  int res = context.run();

  if (context.shouldExit()) {
    return res;
  }

  if (argc > 2) {
    std::cerr << "unknown arguments" << std::endl;
    // https://man.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+4.3-RELEASE&format=html
    return 64; // EX_USAGE: "The command was used incorrectly"
  }

  // repl or stdin
  if (argc == 1) {
    std::string line;

    while (true) {
      global_status_flag = 0; //reset status

      // print a prompt and read from stdin
      std::cout << "lmnt> ";
      std::getline(std::cin, line);

      // handle Ctrl+C
      if (std::cin.fail() and global_status_flag > 0) {
        std::cin.clear(); //reset eof state
        std::cout << std::endl;
        continue;
      }

      // handle Ctrl+D
      if (std::cin.eof()) {
        break;
      }

      // happy path
      std::cout << line << std::endl;
    }
  }

  // string
  if (argc == 2)
    run(std::string(argv[1]));

  return 0;
}

// // add test cases here for main
// TEST_CASE("testing the factorial function") {
//   CHECK(factorial(0) == 1);
//   CHECK(factorial(1) == 1);
//   CHECK(factorial(2) == 2);
//   CHECK(factorial(3) == 6);
//   CHECK(factorial(10) == 3628800);
// }
