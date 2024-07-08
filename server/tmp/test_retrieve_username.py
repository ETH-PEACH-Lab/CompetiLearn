import pandas as pd
import os
def get_username(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['UserName']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['UserName']
    else:
        print("No username found.")
        return "default"

def get_profile_image_path(username):
    profile_images_dir = 'F:/Desktop/PHD/RAG_project/RAG_project5/profile_images_10737'
    image_path = os.path.join(profile_images_dir, f"{username}.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(profile_images_dir, "default.jpg")
    return image_path

def get_kernel_vote(kernel_version_id0):
    kernel_version_id = int(kernel_version_id0)
    middle_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/middle_file3.csv')
    result = middle_df.loc[middle_df['CurrentKernelVersionId'] == kernel_version_id, ['TotalVotes']]
    if not result.empty:
        user_info = result.iloc[0].to_dict()
        return user_info['TotalVotes']
    else:
        print("No votes found.")
        return 0

# Example usage
example_id = 48198250
print(f"username: {get_username(example_id)}")
print(f"Votes: {get_kernel_vote(example_id)}")
# print(f"Views: {get_kernel_view(example_id)}")
print(f"Profile image path: {get_profile_image_path(get_username(example_id))}")
