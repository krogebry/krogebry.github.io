#!/usr/bin/env ruby
require 'pp'

fib_array = [1, 1]
num_fib_iterations = 15

num_fib_iterations.times do |i|
  a = fib_array[i]
  b = fib_array[i+1]
  result = a + b
  fib_array.push( result )
end

pp fib_array
