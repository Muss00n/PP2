import shutil
import os

source = "sample.txt"
destination = "sample_backup.txt"

# Task 4: Copy and back up files using shutil
if os.path.exists(source):
    shutil.copy(source, destination)
    print(f"Backup created: {destination}")
else:
    print("Source file not found.")

# Task 5: Delete files safely
file_to_delete = "sample_backup.txt"

if os.path.exists(file_to_delete):
    os.remove(file_to_delete)
    print(f"{file_to_delete} has been deleted safely.")
else:
    print("Delete failed: File does not exist.")