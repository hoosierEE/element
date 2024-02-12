// from here:
// https://gist.github.com/clwyatt/58169c7b0053c49cc36cca67f4c77cdc

#include <csignal>
#include <cstdlib>

// This is an example of how to to trap Ctrl-C in a cross-platform manner
// it creates a simple REPL event loop and shows how to interrupt it.

// This global is needed for communication between the signal handler
// and the rest of the code. This atomic integer counts the number of times
// Ctrl-C has been pressed by not reset by the REPL code.
volatile sig_atomic_t global_status_flag = 0;

// *****************************************************************************
// install a signal handler for Ctrl-C on Windows
// *****************************************************************************
#if defined(_WIN64) || defined(_WIN32)
#include <windows.h>

// this function is called when a signal is sent to the process
BOOL WINAPI interrupt_handler(DWORD fdwCtrlType) {

  switch (fdwCtrlType) {
  case CTRL_C_EVENT: // handle Ctrl-C
    // if not reset since last call, exit
    if (global_status_flag > 0) {
      exit(EXIT_FAILURE);
    }
    ++global_status_flag;
    return TRUE;

  default:
    return FALSE;
  }
}

// install the signal handler
inline void install_handler() { SetConsoleCtrlHandler(interrupt_handler, TRUE); }
// *****************************************************************************

// *****************************************************************************
// install a signal handler for Ctrl-C on Unix/Posix
// *****************************************************************************
#elif defined(__APPLE__) || defined(__linux) || defined(__unix) ||  \
  defined(__posix)
#include <unistd.h>

// this function is called when a signal is sent to the process
void interrupt_handler(int signal_num) {

  if(signal_num == SIGINT){ // handle Ctrl-C
    // if not reset since last call, exit
    if (global_status_flag > 0) {
      exit(EXIT_FAILURE);
    }
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
#endif
// *****************************************************************************


// *****************************************************************************
// This is the main program, a simple REPL with a command called "go" that just
// spins in a loop, unless interrupted, and a command "exit" to exit the program
// *****************************************************************************

#include <iostream>
#include <string>

int main(int argc, char *argv[]) {

  // call the platform-specific code
  install_handler();

  // the REPL
  while (true) {
    // reset the status flag
    global_status_flag = 0;

    // print a prompt and read from stdin
    std::cout << "prompt> ";
    std::string input;
    getline(std::cin, input);
    // clear stdin if interrupted
    if (std::cin.fail() || std::cin.eof()) {
      std::cin.clear(); // reset cin state
      input.clear(); //clear input string
      std::cout << "Interrupted stdin.\n";
    }
    else{
      std::cout << input << "\n";
    }

    if (input == "go") {
      // a simple busy loop that checks the flag
      while (true) {
        if (global_status_flag > 0){
          std::cout << "Interrupted go command.\n";
          break;
        }
      }
    }

    if (input == "exit") {
      break;
    }
  }

  return EXIT_SUCCESS;
}
