import shutil
import os

# Setup names
source_file = "test.txt"
destination_folder = "backups"

# Create a test file if it doesn't exist
if not os.path.exists(source_file):
    with open(source_file, "w") as f:
        f.write("Moving this file.")

# Ensure destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Task 4: Move/Copy files between directories
# Use shutil.copy to keep the original, or shutil.move to relocate it
try:
    shutil.move(source_file, f"{destination_folder}/{source_file}")
    print(f"Moved '{source_file}' to '{destination_folder}/'")
except Exception as e:
    print(f"Error: {e}")