import os

path = "data/logs/2026"
os.makedirs(path, exist_ok=True)
print(f"Directory structure created: {path}")

with open(f"{path}/log.txt", "w") as f:
    f.write("Log entry")

print("\n--- Current Directory Listing ---")
items = os.listdir(".")
for item in items:
    print(item)

print("\n--- Python Files Found ---")
for file in os.listdir("."):
    if file.endswith(".py"):
        print(file)