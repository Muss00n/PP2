# Task 1: Create a text file and write sample data
filename = "sample.txt"

with open(filename, "w") as file:
    file.write("This is line 1.\n")
    file.write("This is line 2.\n")
print(f"{filename} created and written.")

# Task 3: Append new lines and verify content
