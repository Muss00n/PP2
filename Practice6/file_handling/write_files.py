filename = "sample.txt"

with open(filename, "w") as file:
    file.write("This is line 1.\n")
    file.write("This is line 2.\n")
print(f"{filename} created and written.")

