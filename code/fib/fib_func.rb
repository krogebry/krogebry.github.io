#!/usr/bin/env ruby
require 'pp'

num_fib_iterations = 15

def fib(num_fib_iterations=1)
  fib_array = [1, 1]
  num_fib_iterations.times do |i|
    a = fib_array[i]
    b = fib_array[i+1]
    result = a + b
    fib_array.push( result )
  end
  return fib_array
end

pp fib(num_fib_iterations)
