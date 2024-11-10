import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from job_scraper_utils import *
import json
from openai import OpenAI

load_dotenv()


api_key = os.getenv('OPENAI_API_KEY')
united_states = 'https://www.indeed.com'

country = united_states

driver = configure_webdriver()
job_position = 'devops engineer'
# job_positions = ['devops engineer', 'security engineer', 'cloud engineer', 'backend', 'AWS', 'Terraform', 'Gitlab', 'Python', 'Docker', 'Bash', 'systems enginer', 'software engineer']
job_positions = ['terraform']
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

# Concatenate all dataframes and remove duplicates
merged_df = pd.concat(dataframes).drop_duplicates().reset_index(drop=True)

merged_df.to_json(filename, orient='records')

json_data = merged_df.to_json(orient="records")

# Parse and pretty-print JSON
parsed_json = json.loads(json_data)
with open(filename, "w") as f:
    json.dump(parsed_json, f, indent=4)



# We want to create a function that adds the job description in the JSON output

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



print(jobDescription('https://www.indeed.com/rc/clk?jk=56da6e5acbeb0d81&bb=qpWnEreCP8py8fL5SNfQwAbrTTkJU78Lb1aLYFitamL_QG1nwMmsm1WCHcVV7vK1EIAxF_ZiksxaAozW_5TUkIwjWhiIwM3YVZoC0o3xZOLgq3JPs8_oGSco3HLxCy2E&xkcb=SoDZ67M35KbfTTgJAL0JbzkdCdPP&fccid=a0ba1788fee5b9f4&vjs=3'))


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

    # Extracting the resume content from the response
    print('response = ', response.choices[0].message.content)
    # for k in response:
    #     print('k = ', k)
    #     print(response[k])
    # resume = response['choices'][0]['message']['content']
    return 'END'

# Example job description
job_description = """
Principal Technical Consultant, Platform Engineering
Serving as a technical thought leader and SME for our ecosystem of partners, customers, and service providers in the realm of Modern Apps & Platform Engineering, in addition to serving as a leader of other teammates. The Principal Technical Consultant works as part of the consulting team to lead the development, design, implementation, and engagement leader of client solutions. Principal Technical Consultants manage, mentor and delegate to engineers on a project basis, manage and maintain career advancement plans for the team, and within the broader organization as it relates to internal initiatives and indirect project support. This role requires a strategic mindset, strong leadership abilities, and deep technical proficiency across various domains.
Responsibilities...
"""

# Generate the resume
resume_text = generate_resume(job_description)
print(resume_text)



driver.quit()