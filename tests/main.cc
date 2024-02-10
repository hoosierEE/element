#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h"

#include <iostream>

using namespace std;

int factorial(int number) {
  return number <= 1 ? number : factorial(number - 1) * number;
  // return number > 1 ? factorial(number - 1) * number : 1;
}

int main(int argc, char *argv[]) {
  doctest::Context context;
  context.setOption("minimal", true);
  context.applyCommandLine(argc,argv);

  int res = context.run();

  if (context.shouldExit())
    return res;

  for (int i=0;i<argc; i++)
    cout << argv[i] << endl;

  return 0;
}

TEST_CASE("testing the factorial function") {
  CHECK(factorial(0) == 1);
  CHECK(factorial(1) == 1);
  CHECK(factorial(2) == 2);
  CHECK(factorial(3) == 6);
  CHECK(factorial(10) == 3628800);
}
