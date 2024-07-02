import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
import time

# Function to download an image from a URL and save it to a specified path
def download_image(img_url, save_path):
    try:
        img_data = requests.get(img_url).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        print(f"Error downloading image from {img_url}: {e}")

# Function to check if the image has already been downloaded
def image_already_downloaded(save_path):
    return os.path.exists(save_path)

# Define the paths
original_csv_file_path = r'F:\Desktop\PHD\RAG_project\RAG_project5\middle_file3.csv'
temp_csv_file_path = r'F:\Desktop\PHD\RAG_project\RAG_project5\unique_usernames.csv'
image_save_directory = r'F:\Desktop\PHD\RAG_project\RAG_project5\profile_images'

# Create the directory to save images if it does not exist
os.makedirs(image_save_directory, exist_ok=True)

# Load the original CSV file and extract unique user names
df = pd.read_csv(original_csv_file_path)
unique_usernames_df = df[['UserName']].drop_duplicates()

# Save the unique user names to a temporary CSV file
unique_usernames_df.to_csv(temp_csv_file_path, index=False)

# Read the temporary CSV file with unique user names
unique_usernames_df = pd.read_csv(temp_csv_file_path)

# Initialize the WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode for efficiency
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Iterate over the rows in the unique user names DataFrame
for index, row in unique_usernames_df.iterrows():
    user_name = row['UserName']
    profile_url = f"https://www.kaggle.com/{user_name}"
    img_save_path = os.path.join(image_save_directory, f"{user_name}.jpg")
    
    # Check if the image has already been downloaded
    if image_already_downloaded(img_save_path):
        print(f"Image for {user_name} already downloaded. Skipping...")
        continue
    
    try:
        # Open the Kaggle profile page
        driver.get(profile_url)
        time.sleep(2)  # Wait for the page to load completely
        
        # Find the div tag that contains the profile picture URL
        div_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="avatar-image"]')
        style = div_tag.get_attribute('style')
        
        # Use regex to find the URL within the style attribute
        match = re.search(r'url\("?(.*?)"?\)', style)
        if match:
            img_url = match.group(1)
            if img_url == "/static/images/profile/default-avatar.png":
                print(f"Skipping default avatar for {user_name}.")
                continue
            
            print(f"Downloading image for {user_name} from {img_url}")
            
            # Download the image
            download_image(img_url, img_save_path)
        else:
            print(f"Profile picture URL not found in the style attribute for {user_name}.")
    except Exception as e:
        print(f"Error processing profile for {user_name}: {e}")

# Close the WebDriver
driver.quit()
