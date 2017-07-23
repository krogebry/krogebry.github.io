#!/usr/bin/env ruby

def calc_fib(n)
  n == 0 || n == 1 ? n : calc_fib(n-2) + calc_fib(n-1)
end
puts calc_fib(15)

