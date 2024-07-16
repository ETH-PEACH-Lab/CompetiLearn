import pandas as pd
from tqdm import tqdm

# Paths to the CSV files
kernels_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/Kernels.csv'
users_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/Users.csv'
kernel_versions_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/KernelVersions.csv'
kernel_version_sources_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/KernelVersionKernelSources.csv'
submissions_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/Submissions.csv'
# filtered_submissions_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/FilteredSubmissions.csv'
intermediate_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/middle_file3.csv'
# final_output_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/FinalOutput.csv'

# Load the initial CSV files
kernels_df = pd.read_csv(kernels_path)
users_df = pd.read_csv(users_path)
kernel_versions_df = pd.read_csv(kernel_versions_path)
kernel_version_sources_df = pd.read_csv(kernel_version_sources_path)
submissions_chunk_size = 100000  # Define the chunk size for processing

# Print initial shapes
print(f"kernels_df shape: {kernels_df.shape}")
print(f"users_df shape: {users_df.shape}")
print(f"kernel_versions_df shape: {kernel_versions_df.shape}")
print(f"kernel_version_sources_df shape: {kernel_version_sources_df.shape}")

# Merge the dataframes on AuthorUserId (kernels_df) and Id (users_df)
merged_df = pd.merge(kernels_df, users_df, left_on='AuthorUserId', right_on='Id', how='left')

# Select and rename the required columns
middle_df = merged_df[['Id_x', 'TotalVotes', 'TotalViews', 'TotalComments', "MadePublicDate", 'CurrentKernelVersionId', 'AuthorUserId', 'UserName', 'CurrentUrlSlug']]
middle_df.columns = ['KernelId', 'TotalVotes', 'TotalViews', 'TotalComments', "MadePublicDate", 'CurrentKernelVersionId', 'AuthorUserId', 'UserName', 'CurrentUrlSlug']

# Merge with kernel_versions_df on CurrentKernelVersionId (middle_df) and Id (kernel_versions_df)
merged_with_kernel_versions_df = pd.merge(middle_df, kernel_versions_df[['Id', 'Title']], left_on='CurrentKernelVersionId', right_on='Id', how='left')

# Drop the extra 'Id' column
merged_with_kernel_versions_df = merged_with_kernel_versions_df.drop(columns=['Id'])

# Print shape after first merge
# Save the intermediate result to a CSV file
merged_with_kernel_versions_df.to_csv(intermediate_path, index=False)
print("Intermediate file created successfully.")