import os
import json
from collections import Counter
import shutil

def identify_notebook_language(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        
        kernelspec = notebook_content.get('metadata', {}).get('kernelspec', {})
        language = kernelspec.get('language', 'Unknown')
        return language
    except Exception as e:
        print(f"Error reading {notebook_path}: {e}")
        return 'Unknown'

def summarize_languages_in_folder_and_copy_python(folder_path, destination_folder):
    language_counter = Counter()
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = os.path.join(root, file)
                language = identify_notebook_language(notebook_path)
                language_counter[language] += 1
                
                if language == 'python':
                    destination_path = os.path.join(destination_folder, os.path.relpath(notebook_path, folder_path))
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    shutil.copy2(notebook_path, destination_path)
    
    return language_counter

# Example usage:
folder_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter_python'
destination_folder = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter_python'
language_summary = summarize_languages_in_folder_and_copy_python(folder_path, destination_folder)

print("Language statistics:")
for language, count in language_summary.items():
    print(f"{language}: {count} files")
