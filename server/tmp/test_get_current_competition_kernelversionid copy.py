import os
import pandas as pd

# Specify the directory containing the .ipynb files
directory = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/competition_10737_filter_python'

# Initialize an empty list to store the file names
file_names = []

# Loop through the files in the specified directory
for file in os.listdir(directory):
    if file.endswith('.ipynb'):
        # Get the file name without the .ipynb extension
        file_name = os.path.splitext(file)[0]
        # Append the file name to the list
        file_names.append(file_name)

# Create a DataFrame from the list of file names
df = pd.DataFrame(file_names, columns=['kernelversionid'])

# Specify the output CSV file path
output_csv = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/10737_kernelversionid.csv'

# Export the DataFrame to a CSV file
df.to_csv(output_csv, index=False)

print(f"CSV file has been created at {output_csv}")
