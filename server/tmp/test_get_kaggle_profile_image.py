from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

# Define the URL of the Kaggle profile page
profile_url = "https://www.kaggle.com/harutot"

# Initialize the WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode for efficiency
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the Kaggle profile page
driver.get(profile_url)

# Find the div tag that contains the profile picture URL
try:
    div_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="avatar-image"]')
    style = div_tag.get_attribute('style')

    # Use regex to find the URL within the style attribute
    match = re.search(r'url\("?(.*?)"?\)', style)
    if match:
        img_url = match.group(1)
        print(f"Profile picture URL: {img_url}")
    else:
        print("Profile picture URL not found in the style attribute.")
except Exception as e:
    print(f"Error: {e}")

# Close the WebDriver
driver.quit()
