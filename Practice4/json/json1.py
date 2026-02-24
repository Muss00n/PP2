import json
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "sample-data.json")

with open(file_path, "r") as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 50 + " " + "-" * 20 + "  " + "------" + "  " + "------")


for item in data.get('imdata', []):
    attrs = item.get('l1PhysIf', {}).get('attributes', {})
    dn = attrs.get('dn', '')
    descr = attrs.get('descr', '')
    speed = attrs.get('speed', 'inherit')
    mtu = attrs.get('mtu', '')
    

    print(f"{dn:<50} {descr:<20} {speed:<7} {mtu:<6}")