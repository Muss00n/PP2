import shutil
import os

source_file = "test.txt"
destination_folder = "backups"

if not os.path.exists(source_file):
    with open(source_file, "w") as f:
        f.write("Moving this file.")

os.makedirs(destination_folder, exist_ok=True)

try:
    shutil.move(source_file, f"{destination_folder}/{source_file}")
    print(f"Moved '{source_file}' to '{destination_folder}/'")
except Exception as e:
    print(f"Error: {e}")