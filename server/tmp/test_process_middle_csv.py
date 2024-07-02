import pandas as pd

# Load the CSV files

kernels_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/Kernels.csv')
users_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/Users.csv')
# Merge the dataframes on AuthorUserId (kernels_df) and Id (users_df)
merged_df = pd.merge(kernels_df, users_df, left_on='AuthorUserId', right_on='Id', how='left')

# Select and rename the required columns
middle_df = merged_df[['Id_x', 'TotalVotes','TotalViews','CurrentKernelVersionId','AuthorUserId', 'UserName', 'CurrentUrlSlug']]
middle_df.columns = ['KernelId','TotalVotes','TotalViews','CurrentKernelVersionId', 'AuthorUserId', 'UserName', 'CurrentUrlSlug']

# Save to a new CSV file
middle_df.to_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv', index=False)

print("Middle file created successfully.")
