import pandas as pd

# Load the 10737 file
file_10737_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/10737_kernelversionid.csv'
df_10737 = pd.read_csv(file_10737_path)

# Load the kernelversionkernelsources file
kernelversionkernelsources_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/KernelVersionKernelSources.csv'
df_kernelversionkernelsources = pd.read_csv(kernelversionkernelsources_path)

# Convert the matching attributes to integers
df_10737['kernelversionid'] = df_10737['kernelversionid'].astype(int)
df_kernelversionkernelsources['KernelVersionId'] = df_kernelversionkernelsources['KernelVersionId'].astype(int)

# Perform a left join on the two dataframes
merged_df = pd.merge(df_10737, df_kernelversionkernelsources, left_on='kernelversionid', right_on='KernelVersionId', how='left')

# Specify the output file path for the merged dataframe
output_csv_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/10737_kernelsourceid.csv'

# Save the merged dataframe to a CSV file
merged_df.to_csv(output_csv_path, index=False)

# Count the total number of rows
total_rows = len(merged_df)

# Count the number of rows where SourceKernelVersionId is not empty
non_empty_sourcekernelversionid_rows = merged_df['SourceKernelVersionId'].notna().sum()

print(f"Merged CSV file has been created at {output_csv_path}")
print(f"Total number of rows: {total_rows}")
print(f"Number of rows with non-empty SourceKernelVersionId: {non_empty_sourcekernelversionid_rows}")
