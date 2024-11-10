import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from job_scraper_utils import *
import json
from openai import OpenAI
from datetime import datetime

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
united_states = 'https://www.indeed.com'
country = united_states

driver = configure_webdriver()
# job_positions = ['devops engineer', 'security engineer', 'cloud engineer', 'backend', 'AWS', 'Terraform', 'Gitlab', 'Python', 'Docker', 'Bash', 'systems enginer', 'software engineer']
job_positions = ['terraform']
job_location = '90066'
date_posted = 1
pay = '$150,000'
sorted_df = None

today_date = datetime.today().strftime('%Y-%m-%d')
filename = f"{today_date}.json"
full_url = search_jobs(pay, driver, country, 'devops engineer', job_location, date_posted)
df = scrape_job_data(driver, country)
dataframes = []
for job_position in job_positions:
    full_url = search_jobs(pay, driver, country, job_position, job_location, date_posted)
    df = scrape_job_data(driver, country)
    dataframes.append(df)

# Concatenate all dataframes and remove duplicates
merged_df = pd.concat(dataframes).drop_duplicates().reset_index(drop=True)
merged_df.to_json(filename, orient='records')
json_data = merged_df.to_json(orient="records")
# Parse and pretty-print JSON
parsed_json = json.loads(json_data)
with open(filename, "w") as f:
    json.dump(parsed_json, f, indent=4)


# This function takes a URL and returns the full description as a string.
def jobDescription(url):
    driver.get(url)
    description_element = driver.find_element(By.XPATH, '//div[contains(@class, "jobsearch-JobComponent-description")]')
    description = description_element.text
    start_index = description.find("Full job description")
    if start_index != -1:
        description = description[start_index:]
    else:
        description = description
    return description


def generate_resume(job_description):
    prompt = f"""
    Create a professional resume for a job application based on the following job description:

    Job Title: Principal Technical Consultant, Platform Engineering

    Job Description:
    {job_description}

    Format the resume as follows:
    - Contact Information (Name, Email, Phone Number, LinkedIn Profile)
    - Professional Summary
    - Key Skills
    - Professional Experience (include 2-3 job experiences with responsibilities and accomplishments)
    - Certifications
    - Education
    - Projects (if relevant)
    - Additional Information (optional)

    Ensure the resume highlights relevant skills like Platform Engineering, CI/CD, DevSecOps, Cloud Infrastructure, client relationship management, and leadership. 
    """
    client = OpenAI(api_key=api_key)
    # completion = client.chat.completions.create(
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who creates professional resumes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    print('response = ', response.choices[0].message.content)
    return 'END'


# Generate the resume
description = jobDescription('https://www.indeed.com/viewjob?jk=61346edc64651631&from=serp&vjs=3')
resume_text = generate_resume(description)
print(resume_text)

driver.quit()

base_resume = """
Booz Allen Hamilton Staff Engineer | Sept. 2022 – Present Aug. 2020 – Present
Remote
▪ Full Services Team - Hybrid Legacy Application Migration to AWS.
o Increased scalability and reliability of 6+ applications by 40%, migrating
hybrid infrastructure to AWS ECS, ECR, RDS, and MQ with Terraform.
o Reduced end-to-end application deployment time and manual steps by 50% using
Gitlab CI, Docker, and Terraform.
o Integrated Artifactory with AWS ECR for container image storage, simplifying
artifact management and versioning for 20+ Dockerized applications.
▪ Security Services Team - Deployed and Maintained Security Infrastructure.
o Deployed and maintained Tenable SC and Trend Micro across 10+ multi-region AWS
accounts, significantly decreased vulnerabilities by automating security scans.
o Improved the patching process for security assets which saved 5 hours a week by
automating updates using AWS Inspector, Lambda, and Step Functions.
Software Engineer | Dec. 2020 – Sept. 2022
▪ Foundational Services Team
o Automated TLS certificate creation by developing a Gitlab CI pipeline leveraging
AWS ACM across 50+ instances.
▪ Systems Engineer | Aug. 2020 - Dec. 2020
o Developed a web scraping Python bot that saved 160+ hours of manual data entry
by curling client financial data into an Excel spreadsheet.
o Researched and drafted proposals for Cloud Engineering and FedRAMP projects for
the Department of Defense.
"""