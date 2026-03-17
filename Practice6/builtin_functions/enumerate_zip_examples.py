fruits = ["apple", "banana", "cherry"]
print("--- Enumerate Example ---")
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}: {fruit}")

prices = [1.2, 0.5, 2.5]
print("\n--- Zip Example ---")
for fruit, price in zip(fruits, prices):
    print(f"The {fruit} costs ${price}")

value = "100"
if isinstance(value, str):
    num_value = int(value)
    print(f"\nConverted {type(value)} to {type(num_value)}")
    print(f"Result: {num_value + 50}")