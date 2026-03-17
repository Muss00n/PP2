from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

doubled = list(map(lambda x: x * 2, numbers))
print(f"Mapped (Doubled): {doubled}")

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Filtered (Evens): {evens}")

product = reduce(lambda x, y: x * y, numbers)
print(f"Reduced (Product): {product}")