#!/usr/bin/python3
import os

# Function to count 'ZN' occurrences in a file
def count_zn_frequency(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content.count('ZN')  # Count case-sensitive occurrences
    except FileNotFoundError:
        return 0

# Define the folder paths
code_folder = 'Assets/Codes'
md_folder = 'MdFiles'
images_folder = 'Assets/Images'

# Initialize lists to store file paths
code_files = []
md_files = []
images = []

# Fetch code files from the code folder
if os.path.exists(code_folder):
    for file in sorted(os.listdir(code_folder)):
        # Extendable list of code extensions
        if file.endswith(('.py', '.cpp', '.wls')): 
            code_files.append(file)

# Fetch markdown files from the MdFiles folder
if os.path.exists(md_folder):
    for file in sorted(os.listdir(md_folder)):
        if file.endswith('.md'):
            md_files.append(file)

# Fetch images from Images folder
if os.path.exists(images_folder):
    for file in sorted(os.listdir(images_folder)):
        if file.endswith(('.png', '.svg')):
            images.append(file)

# Create the content for the Markdown file
content = "# MdFiles\n\n"
for file in md_files:
    file_path = os.path.join(md_folder, file)
    zn_count = count_zn_frequency(file_path)
    content += f"- [[MdFiles/{file}|{file.replace('.md', '')}]] (ZN Count: {zn_count})\n"

content += "\n\n# Codes\n\n"
content += "\n".join([f"- [[Assets/Codes/{file}|{os.path.splitext(file)[0]}]]" for file in code_files])

content += "\n\n# Images\n\n"
content += "\n".join([f"- [[Assets/Images/{file}|{os.path.splitext(file)[0]}]]" for file in images])

# Save the content to a new Markdown file
output_path = 'Content.md'
with open(output_path, 'w') as f:
    f.write(content)

print(f"Content has been saved to {output_path}.")
