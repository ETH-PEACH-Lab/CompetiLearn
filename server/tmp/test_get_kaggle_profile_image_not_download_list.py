import pandas as pd
import os

# Define the paths
original_csv_file_path = r'F:\Desktop\PHD\RAG_project\RAG_project5\middle_file3.csv'
image_save_directory = r'F:\Desktop\PHD\RAG_project\RAG_project5\profile_images'
not_downloaded_csv_path = r'F:\Desktop\PHD\RAG_project\RAG_project5\not_downloaded_usernames.csv'

# Load the original CSV file
df = pd.read_csv(original_csv_file_path)

# Extract the unique usernames
unique_usernames = df['UserName'].unique()

# Function to check if an image has already been downloaded
def image_already_downloaded(username):
    img_save_path = os.path.join(image_save_directory, f"{username}.jpg")
    return os.path.exists(img_save_path)

# Filter out the usernames for which images have already been downloaded
not_downloaded_usernames = [username for username in unique_usernames if not image_already_downloaded(username)]

# Create a DataFrame for the usernames that haven't been downloaded yet
not_downloaded_df = pd.DataFrame(not_downloaded_usernames, columns=['UserName'])

# Save the DataFrame to a CSV file
not_downloaded_df.to_csv(not_downloaded_csv_path, index=False)

print(f"List of usernames that haven't been downloaded yet saved to {not_downloaded_csv_path}")
