import os

# Task 1: Create nested directories
# 'exist_ok=True' prevents an error if the folder already exists
path = "data/logs/2026"
os.makedirs(path, exist_ok=True)
print(f"Directory structure created: {path}")

# (Optional) Creating a dummy file to list later
with open(f"{path}/log.txt", "w") as f:
    f.write("Log entry")

# Task 2: List files and folders in the current directory
print("\n--- Current Directory Listing ---")
items = os.listdir(".")
for item in items:
    print(item)

# Task 3: Find files by extension (e.g., .py)
print("\n--- Python Files Found ---")
for file in os.listdir("."):
    if file.endswith(".py"):
        print(file)