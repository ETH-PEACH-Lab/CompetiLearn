import os
import shutil
import pandas as pd

# Define the paths
csv_file_path = 'F:\Desktop\PHD\RAG_project\RAG_project2\Kernels.csv'
source_folder = 'F:\Desktop\PHD\RAG_project\RAG_project2\competition_19988'
destination_folder = 'F:\Desktop\PHD\RAG_project\RAG_project2\competition_19988_filter'

# Read the CSV file
kernels_df = pd.read_csv(csv_file_path)

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Iterate through each CurrentKernelVersionId in the CSV
for kernel_id in kernels_df['CurrentKernelVersionId']:
    # Convert the kernel_id to string and remove the .0 if it exists
    kernel_id_str = str(kernel_id).replace('.0', '')
    
    # Define the source and destination file paths
    source_file = os.path.join(source_folder, f'{kernel_id_str}.ipynb')  # assuming the files are .ipynb
    destination_file = os.path.join(destination_folder, f'{kernel_id_str}.ipynb')
    
    # Check if the source file exists before copying
    if os.path.exists(source_file):
        shutil.copy2(source_file, destination_file)
        print(f'Copied: {source_file} to {destination_file}')
    else:
        print(f'File not found: {source_file}')

print('Copy operation completed.')