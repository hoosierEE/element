#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h" //https://github.com/doctest/doctest

#include "runtime.h" //Runtime
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iostream>

// https://man.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+4.3-RELEASE&format=html
#define EX_USAGE 64 //The command was used incorrectly
#define EX_DATAERR 65 //The input data was incorrect in some way.
#define EX_NOINPUT 66 //An input file did not exist or was not readable.
#define EX_IOERR 74 //An error occurred while doing I/O on some file.
#define EX_NOHOST 68 //The host specified did not exist.

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

  // handle --help -h for application before passing remaining args to doctest
  for (int i=1; i < argc; i++) {
    auto arg = std::string(argv[i]);
    if (arg == "-h" or arg == "--help") {
      std::cout << "help message" << std::endl;
      return 0;
    }
  }

  install_handler(); //handle ^C

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
    return EX_USAGE; //"The command was used incorrectly"
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

      runtime.error(); // display error but don't crash. reset error each loop.

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
          if (runtime.error()) {return EX_DATAERR;}
          runtime.read(line);
          runtime.parse();
          runtime.eval();
          runtime.print();
        }
        // runtime.tokens.push_back(std::make_tuple(runtime.lineNum,0,Runtime::END,""));
      } else {
        std::cerr << "unable to open file" << std::endl;
        return EX_NOINPUT;
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


// TEST_CASE("runtime class") {
//   Runtime rt;
//   rt.read(std::string("hello"));
//   CHECK(rt.line.size() == 5);
// }
