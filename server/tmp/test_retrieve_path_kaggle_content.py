import pandas as pd

# Load the CSV files
kernels_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project2/Kernels.csv')
users_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project2/Users.csv')

# Updated function to include retrieving the username from Users.csv
def get_author_user_id_and_url_slug_with_username(kernel_id):
    # Get the AuthorUserId and CurrentUrlSlug from the kernels dataframe
    kernel_info = kernels_df.loc[kernels_df['Id'] == kernel_id, ['AuthorUserId', 'CurrentUrlSlug']]
    
    if not kernel_info.empty:
        kernel_info = kernel_info.iloc[0].to_dict()
        
        # Get the UserName from the users dataframe based on AuthorUserId
        user_info = users_df.loc[users_df['Id'] == kernel_info['AuthorUserId'], ['UserName']]
        
        if not user_info.empty:
            kernel_info['UserName'] = user_info.iloc[0]['UserName']
            return kernel_info
        else:
            return None
    else:
        return None

# Example usage
example_id = 1
output_with_username = get_author_user_id_and_url_slug_with_username(example_id)
print(output_with_username)
