#ifndef NICEREPL_H_
#define NICEREPL_H_
#include <csignal>

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

#endif // NICEREPL_H_
