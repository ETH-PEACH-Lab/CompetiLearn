import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to download an image from a URL and save it to a specified path
def download_image(img_url, save_path):
    try:
        img_data = requests.get(img_url).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        print(f"Error downloading image from {img_url}: {e}")

# Function to process a single user profile
def process_profile(user_name, driver_path, image_save_directory):
    profile_url = f"https://www.kaggle.com/{user_name}"
    img_save_path = os.path.join(image_save_directory, f"{user_name}.jpg")
    default_img_downloaded = False
    
    try:
        # Initialize the WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for efficiency
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        
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
                print(f"Default avatar found for {user_name}.")
                if not default_img_downloaded:
                    download_image("https://www.kaggle.com/static/images/profile/default-avatar.png", os.path.join(image_save_directory, "default.jpg"))
                    default_img_downloaded = True
                print(f"Current just finished photo: {user_name}")
                driver.quit()
                return
            
            print(f"Downloading image for {user_name} from {img_url}")
            # Download the image
            download_image(img_url, img_save_path)
        else:
            print(f"Profile picture URL not found in the style attribute for {user_name}.")
    except Exception as e:
        print(f"Error processing profile for {user_name}: {e}")
    finally:
        print(f"Current just finished photo: {user_name}")
        driver.quit()

# Define the paths
image_save_directory = r'/Users/junlingwang/myfiles/PHD/RAG_project/CompetiLearn/data/profile_images_10737'
driver_path = ChromeDriverManager().install()

# Create the directory to save images if it does not exist
os.makedirs(image_save_directory, exist_ok=True)

# Read the CSV file with unique user names
unique_usernames_df = pd.read_csv('F:/Desktop/PHD/RAG_project/RAG_project5/usernames_for_competition.csv')

# Use ThreadPoolExecutor to process profiles concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_profile, user_name, driver_path, image_save_directory) for user_name in unique_usernames_df['UserName']]
    
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error: {e}")
