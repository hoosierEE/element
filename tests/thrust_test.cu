#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/generate.h>
#include <thrust/reduce.h>
#include <thrust/functional.h>
#include <thrust/random.h>

// Example code from here: https://github.com/NVIDIA/cccl/tree/main/thrust
//
// NOTE: this did not compile at first.
// Fix header file using suggestion from here:
// https://github.com/NVIDIA/nccl/issues/650#issuecomment-1145173577

int main() {
  // Generate random data serially.
  thrust::default_random_engine rng(1337);
  thrust::uniform_real_distribution<double> dist(-50.0, 50.0);
  thrust::host_vector<double> h_vec(32 << 20);
  thrust::generate(h_vec.begin(), h_vec.end(), [&] { return dist(rng); });

  // Transfer to device and compute the sum.
  thrust::device_vector<double> d_vec = h_vec;
  double x = thrust::reduce(d_vec.begin(), d_vec.end(), 0, thrust::plus<int>());
  std::cout << x << std::endl;
}
