from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# Task 1: map() - Multiply every number by 2
doubled = list(map(lambda x: x * 2, numbers))
print(f"Mapped (Doubled): {doubled}")

# Task 1: filter() - Keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Filtered (Evens): {evens}")

# Task 2: reduce() - Multiply all numbers together (1*2*3*4*5*6)
product = reduce(lambda x, y: x * y, numbers)
print(f"Reduced (Product): {product}")