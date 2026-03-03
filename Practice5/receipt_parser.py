import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "raw.txt")

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

pattern = r"ab*"
matches = re.findall(pattern, text)
print("1:", matches)


pattern = r"ab{2,3}"
matches = re.findall(pattern, text)
print("2:", matches)


pattern = r"\b[a-z]+_[a-z]+\b"
matches = re.findall(pattern, text)
print("3:", matches)



pattern = r"\b[A-Z][a-z]+\b"
matches = re.findall(pattern, text)
print("4:", matches)


pattern = r"a.*b"
matches = re.findall(pattern, text)
print("5:", matches)



pattern = r"[ ,.]"
result = re.sub(pattern, ":", text)
print("6:", result)



def snake_to_camel(match):
    return match.group(1).upper()
result = re.sub(r"_([a-z])", snake_to_camel, text)
print("7:", result)


pattern = r"(?=[A-Z])"
result = re.split(pattern, text)
print("8:", result)



pattern = r"(?<!^)(?=[A-Z])"
result = re.sub(pattern, " ", text)
print("9:", result)



pattern = r"(?<!^)(?=[A-Z])"
result = re.sub(pattern, "_", text).lower()
print("10:", result)