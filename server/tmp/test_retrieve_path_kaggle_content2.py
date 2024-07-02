import pandas as pd

# Load the middle file
middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project2/middle_file2.csv')

# Define the function to get the URL by KernelId
def get_kernel_url(kernel_version_id):
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['UserName', 'CurrentUrlSlug']]
    print(result)
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        url = f"https://www.kaggle.com/code/{user_info['UserName']}/{user_info['CurrentUrlSlug']}"
        print(url)
        return url
    else:
        print("No URL found.")
        return None

# Example usage
example_kernel_version_id = 48198250
output_url = get_kernel_url(int(example_kernel_version_id))
print(output_url)
