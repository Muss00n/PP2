filename = "sample.txt"

try:
    with open(filename, "r") as file:
        content = file.read()
        print("--- File Contents ---")
        print(content)
except FileNotFoundError:
    print(f"Error: {filename} does not exist. Run write_files.py first!")

with open(filename, "a") as file:
    file.write("This is an appended line.\n")

print("New line appended. Current content:")
with open(filename, "r") as file:
    print(file.read())