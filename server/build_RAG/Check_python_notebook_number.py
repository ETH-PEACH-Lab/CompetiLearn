import os
import json
from collections import Counter

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

def summarize_languages_in_folder(folder_path):
    language_counter = Counter()
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = os.path.join(root, file)
                language = identify_notebook_language(notebook_path)
                language_counter[language] += 1
    
    return language_counter

# Example usage:
folder_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter'
language_summary = summarize_languages_in_folder(folder_path)

print("Language statistics:")
for language, count in language_summary.items():
    print(f"{language}: {count} files")
