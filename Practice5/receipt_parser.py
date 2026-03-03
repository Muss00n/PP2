import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "raw.txt")

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

#Write a Python program that matches a string that has an 'a' followed by zero or more 'b''s.
pattern = r"ab*"
matches = re.findall(pattern, text)
print("1:", matches)

#Write a Python program that matches a string that has an 'a' followed by two to three 'b'.
pattern = r"ab{2,3}"
matches = re.findall(pattern, text)
print("2:", matches)

#Write a Python program to find sequences of lowercase letters joined with a underscore.
pattern = r"\b[a-z]+_[a-z]+\b"
matches = re.findall(pattern, text)
print("3:", matches)


#Write a Python program to find the sequences of one upper case letter followed by lower case letters.
pattern = r"\b[A-Z][a-z]+\b"
matches = re.findall(pattern, text)
print("4:", matches)

#Write a Python program that matches a string that has an 'a' followed by anything, ending in 'b'.
pattern = r"a.*b"
matches = re.findall(pattern, text)
print("5:", matches)


#Write a Python program to replace all occurrences of space, comma, or dot with a colon.
pattern = r"[ ,.]"
result = re.sub(pattern, ":", text)
print("6:", result)


#Write a python program to convert snake case string to camel case string.
def snake_to_camel(match):
    return match.group(1).upper()
result = re.sub(r"_([a-z])", snake_to_camel, text)
print("7:", result)

#Write a Python program to split a string at uppercase letters.
pattern = r"(?=[A-Z])"
result = re.split(pattern, text)
print("8:", result)


#Write a Python program to insert spaces between words starting with capital letters.
pattern = r"(?<!^)(?=[A-Z])"
result = re.sub(pattern, " ", text)
print("9:", result)


#Write a Python program to convert a given camel case string to snake case.
pattern = r"(?<!^)(?=[A-Z])"
result = re.sub(pattern, "_", text).lower()
print("10:", result)