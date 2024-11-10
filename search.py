import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from job_scraper_utils import *
import json

load_dotenv()

united_states = 'https://www.indeed.com'

country = united_states

driver = configure_webdriver()
job_position = 'devops engineer'
job_positions = ['devops engineer', 'security engineer', 'cloud engineer', 'backend', 'AWS', 'Terraform', 'Gitlab', 'Python', 'Docker', 'Bash', 'systems enginer', 'software engineer']
job_location = '90066'
date_posted = 1
pay = '$150,000'

sorted_df = None

from datetime import datetime

# Get today's date in the desired format
today_date = datetime.today().strftime('%Y-%m-%d')  # Format as 'YYYY-MM-DD'
# Construct the filename
filename = f"{today_date}.json"


full_url = search_jobs(pay, driver, country, 'devops engineer', job_location, date_posted)
df = scrape_job_data(driver, country)
# driver.quit()


dataframes = []

for job_position in job_positions:
    full_url = search_jobs(pay, driver, country, job_position, job_location, date_posted)
    df = scrape_job_data(driver, country)
    dataframes.append(df)
driver.quit()

# Concatenate all dataframes and remove duplicates
merged_df = pd.concat(dataframes).drop_duplicates().reset_index(drop=True)

merged_df.to_json(filename, orient='records')

json_data = merged_df.to_json(orient="records")

# Parse and pretty-print JSON
parsed_json = json.loads(json_data)
with open(filename, "w") as f:
    json.dump(parsed_json, f, indent=4)