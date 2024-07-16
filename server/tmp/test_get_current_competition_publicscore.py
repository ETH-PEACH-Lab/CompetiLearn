import pandas as pd

# Load the 10737_kernelsourceid file
kernelsourceid_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/10737_kernelsourceid.csv'
df_kernelsourceid = pd.read_csv(kernelsourceid_path)

# Load the submissions file
submissions_path = '/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/FilteredSubmissions.csv'
df_submissions = pd.read_csv(submissions_path)

# Drop rows with NaNs in the SourceKernelVersionId column
df_kernelsourceid = df_kernelsourceid.dropna(subset=['SourceKernelVersionId'])

# Convert SourceKernelVersionId to integers in both dataframes
df_kernelsourceid['SourceKernelVersionId'] = df_kernelsourceid['SourceKernelVersionId'].astype(int)
df_submissions['SourceKernelVersionId'] = df_submissions['SourceKernelVersionId'].astype(int)

# Select the necessary columns from the submissions file
df_submissions = df_submissions[['SourceKernelVersionId', 'PublicScoreLeaderboardDisplay']]

# Perform a left join to check which SourceKernelVersionId have a corresponding PublicScoreLeaderboardDisplay
final_merged_df = pd.merge(df_kernelsourceid[['SourceKernelVersionId']], df_submissions, on='SourceKernelVersionId', how='left')

# Count the number of rows with a non-empty PublicScoreLeaderboardDisplay
non_empty_publicscoreleaderboarddisplay_rows = final_merged_df['PublicScoreLeaderboardDisplay'].notna().sum()

# Count the total number of rows with SourceKernelVersionId (should be 14)
total_rows_with_sourcekernelversionid = len(df_kernelsourceid)

print(f"Total number of rows with SourceKernelVersionId: {total_rows_with_sourcekernelversionid}")
print(f"Number of rows with non-empty PublicScoreLeaderboardDisplay: {non_empty_publicscoreleaderboarddisplay_rows}")
