

import pandas as pd

# Load the CSV file into a pandas DataFrame
file_path = 'F:/Desktop/PHD/RAG_project/RAG_project2/middle_file2.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Specify the column name that you want to modify
column_name = 'CurrentKernelVersionId'  # Replace with your column name

# Remove the .0 from the values in the specified column
df[column_name] = df[column_name].apply(lambda x: str(x).rstrip('.0'))

# Save the modified DataFrame back to a new CSV file
output_file_path = 'F:/Desktop/PHD/RAG_project/RAG_project2/middle_file2_modified.csv'  # Replace with your output file path
df.to_csv(output_file_path, index=False)

print(f"Modified CSV saved to {output_file_path}")
