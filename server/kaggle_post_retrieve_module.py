import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(current_dir, '../data/middle_file3.csv'))
# Load the middle file
# Define the function to get the URL by KernelId
def get_kernel_url(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    print(kernel_version_id)

    middle_df = pd.read_csv(csv_path)
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
