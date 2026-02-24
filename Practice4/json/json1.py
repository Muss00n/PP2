import json
import os

# Use os to find the file in the same folder as this script
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "sample-data.json")

# Load the data

with open(file_path, "r") as file:
    data = json.load(file)

# Print the Table Header exactly as required
print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 50 + " " + "-" * 20 + "  " + "------" + "  " + "------")

# Access the list inside 'imdata'
for item in data.get('imdata', []):
    # Drill down into the specific attributes for each interface
    attrs = item.get('l1PhysIf', {}).get('attributes', {})
    
    dn = attrs.get('dn', '')
    descr = attrs.get('descr', '')
    speed = attrs.get('speed', 'inherit')
    mtu = attrs.get('mtu', '')
    
    # Print the row with matching column widths
    print(f"{dn:<50} {descr:<20} {speed:<7} {mtu:<6}")