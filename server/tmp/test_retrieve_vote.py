import pandas as pd

def get_kernel_vote(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalVotes']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalVotes']
    else:
        print("No votes found.")
        return None

def get_kernel_view(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalViews']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalViews']
    else:
        print("No views found.")
        return None

# Example usage
example_id = 48198250
print(f"Votes: {get_kernel_vote(example_id)}")
print(f"Views: {get_kernel_view(example_id)}")
