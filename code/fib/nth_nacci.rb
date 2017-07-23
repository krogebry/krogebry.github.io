#!/usr/bin/env ruby
require 'pp'

num_naccis = 3
num_fib_iterations = 15

def make_fib_array(num_naccis)
  Array.new(num_naccis, 1)
end

def make_nacci(num_naccis=2, num_fib_iterations=1)
  if num_naccis < 2
    puts "Unable to run with < 2 naccis"
    exit(1)
  end

  fib_array = make_fib_array(num_naccis)

  num_fib_iterations.times do |i|
    result = 0
    num_naccis.times do |nacci_i|
      result += fib_array[i+nacci_i]
    end
    fib_array.push( result )
  end

  return fib_array
end

pp make_nacci(num_naccis, num_fib_iterations)
