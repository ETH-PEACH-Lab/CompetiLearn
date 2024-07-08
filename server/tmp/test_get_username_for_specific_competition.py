import os
import pandas as pd

# Define the path to the folder containing the .ipynb files and the path to the CSV file
folder_path = 'F:/Desktop/PHD/RAG_project/RAG_project5/competition_profile_images_10737_filter'
csv_file_path = 'F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv'

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Convert CurrentKernelVersionId to integer (if possible)
df['CurrentKernelVersionId'] = df['CurrentKernelVersionId'].apply(lambda x: str(int(float(x))) if '.' in str(x) else str(x))

# Create a dictionary for fast lookup of UserName by CurrentKernelVersionId
id_to_username = dict(zip(df['CurrentKernelVersionId'], df['UserName']))

# Get the list of .ipynb files in the folder
ipynb_files = [f for f in os.listdir(folder_path) if f.endswith('.ipynb')]

# Prepare a list to collect matching rows
matching_rows = []

# Iterate over the .ipynb files and find matches in the CSV
for file in ipynb_files:
    current_kernel_version_id = os.path.splitext(file)[0]
    if current_kernel_version_id in id_to_username:
        user_name = id_to_username[current_kernel_version_id]
        matching_rows.append({'CurrentKernelVersionId': current_kernel_version_id, 'UserName': user_name})

# Create a DataFrame with the matching rows
matching_df = pd.DataFrame(matching_rows)

# Print the matching rows
print(matching_df)

# Optionally, save the matching rows to a new CSV file
output_csv_path = 'F:/Desktop/PHD/RAG_project/RAG_project5/usernames_for_competition.csv'
matching_df.to_csv(output_csv_path, index=False)
