// Perhaps a crazy idea.
// Compiler and interpreter for a K dialect, implemented in cuda C++.
//
// limitations:
//   line length must be < 256
//
// compile:
//   $ nvcc scanner.cu
//
// run a script file:
//   $ ./a.out < filename.ext
//
// eval a string:
//   $ ./a.out "a:7; a*2+3"  # prints 35
//
// start interactive interpreter:
//   $ ./a.out  # start interpreter
#include <iostream>

// ascii [32-127) (note space at start)
//  !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
// wvqvvvvappvvvvavnnnnnnnnnnvpvvvvvnnnnnnnnnnnnnnnnnnnnnnnnnnpvpvvpnnnnnnnnnnnnnnnnnnnnnnnnnnpvpv
// w______________________________________________________________________________________________ whitespace
// __q____________________________________________________________________________________________ quote
// _______a______a________________________________________________________________________________ adverb
// ________________nnnnnnnnnn_______nnnnnnnnnnnnnnnnnnnnnnnnnn______nnnnnnnnnnnnnnnnnnnnnnnnnn____ noun
// ________pp_________________p_______________________________p_p__p__________________________p_p_ punctuation
// _v_vvvv___vvvv_v__________v_vvvvv___________________________v_vv____________________________v_v verb
// A typical CPU scanner is sequential and stateful but we use a different approach here.
// This one breaks scanning into two phases:
// 1. context-free classify each character
// 2. add contextual info to refine class for each char, resulting in tokens
// The scan function below does step 1.

constexpr int LINE_LEN{256};
enum CharClass {END,SPACE,QUOTE,ADVERB,ALPHA,NUMBER,SYMBOL,LP,RP,LS,RS,LC,RC,COLON,DOT,SEM,VERB,UNK};

__global__ void scan(const char *x, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  __shared__ int x[LINE_LEN];
  if (i < n) {
    char c=x[i];
    char d=c|' '; // tolower
    if      (c == ' ')               x[i] = SPACE;
    else if (c == '"')               x[i] = QUOTE;
    else if (c == '\'' or c == '.')  x[i] = ADVERB;
    else if (d >= 'a' and d <= 'z')  x[i] = ALPHA;
    else if (c >= '0' and c <= '9')  x[i] = NUMBER;
    else if (c == '`')               x[i] = SYMBOL;
    else if (c == '(')               x[i] = LP;
    else if (c == ')')               x[i] = RP;
    else if (c == '[')               x[i] = LS;
    else if (c == ']')               x[i] = RS;
    else if (c == '{')               x[i] = LC;
    else if (c == '}')               x[i] = RC;
    else if (c == ':')               x[i] = COLON;
    else if (c == '.')               x[i] = DOT;
    else if (c == ';')               x[i] = SEM;
    else if (c > 32 and c < 127)     x[i] = VERB;
    else                             x[i] = UNK;
  }
  if (i==n)                          x[i] = END;
  __syncthreads();
  refine(x, n);
}

// refinements:
// 1. strings start with " and end with a second "
// 2. \ has special meaning inside strings
// 3.  / (note leading space) is a line comment
// 4. `xyz is a symbol
__device__ void refine(int *x, int n) {
  int i = blockIdx.x * blcokDim.x + threadIdx.x;
  if (i<n and i>0) {
    // if inside quotes and current char is \, escape next char
    // if inside quotes
  }
}


int main(int argc, char*argv[]) {
  int *buf;
  cudaMallocManaged(&buf, LINE_LEN*sizeof(int)); // buffer for current line tokens

  if (argc == 1) { // repl or stdin
    for (std::string line; std::getline(std::cin, line);) {
      auto sz = line.size();

      scan<<<16,2>>>(buf, line.c_str(), sz);
      cudaDeviceSynchronize();

      refine(buf, sz);
      for (auto &c : buf)
        std::cout << c << " ";

      std::cout << std::endl;
    }
    return 0;
  }

  if (argc == 2) { // string eval
    auto line = std::string(argv[1]);
    int sz = line.size();

    scan<<<16,2>>>(buf, line.c_str(), sz);
    cudaDeviceSynchronize();

    for (int i=0;i<sz;i++)
      std::cout << buf[i] << " ";

    std::cout << std::endl;

    cudaFree(buf);
    return 0;
  }
  return 1; // unknown number of args
}
