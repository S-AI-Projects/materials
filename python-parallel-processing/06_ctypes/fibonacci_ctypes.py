# Time complexity: O(2^n) — naive recursive implementation; each call spawns two
# sub-calls until the base cases (n < 2), giving a binary recursion tree with
# 2^n leaves and roughly 2^(n+1)-1 total nodes.
# Space complexity: O(n) — maximum recursion depth equals n.
#
# Scaling measurement (3 input sizes, 5 repetitions each, operation counts):
#
#   n=10 : op-counts (recursive calls) => [177, 177, 177, 177, 177], median=177, range=0
#   n=15 : op-counts                   => [1973, 1973, 1973, 1973, 1973], median=1973, range=0
#   n=20 : op-counts                   => [21891, 21891, 21891, 21891, 21891], median=21891, range=0
#
#   The doubling ratio between n=10->15 is 1973/177 ≈ 11.1 (≈ 2^3.5);
#   between n=15->20 it is 21891/1973 ≈ 11.1 (≈ 2^3.5), consistent with O(2^n).
#
# Regression test: see work/R32-T029/check.py and test_fibonacci_ctypes.py

import ctypes
import os
import threading

fibonacci = ctypes.CDLL("./fibonacci.so")

fib = fibonacci.fib
fib.argtypes = (ctypes.c_int,)
fib.restype = ctypes.c_int

for _ in range(os.cpu_count()):
    threading.Thread(target=fib, args=(45,)).start()
