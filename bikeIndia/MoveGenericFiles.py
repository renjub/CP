import os
import shutil

# Define paths
cwd = os.getcwd()
article_folder = os.path.join(cwd, 'Articles')
generic_folder = os.path.join(article_folder, 'Generic')
list_file_path = 'Generic.list'

# Ensure the Generic folder exists within Article
os.makedirs(generic_folder, exist_ok=True)

# Read the file names from generic.list
try:
    with open(list_file_path, 'r') as file:
        files_to_move = file.read().splitlines()
except FileNotFoundError:
    print(f"Error: {list_file_path} not found.")
    exit(1)

# Move each file listed in generic.list to Article/Generic
for file_name in files_to_move:
    source_path = os.path.join(article_folder, file_name)
    destination_path = os.path.join(generic_folder, file_name)

    if os.path.isfile(source_path):
        shutil.move(source_path, destination_path)
        print(f"Moved: {file_name}")
    else:
        print(f"Warning: {file_name} not found in the Article folder.")
