import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from job_scraper_utils import *
import json
from openai import OpenAI
from datetime import datetime
from docx import Document
# import fitz
import pypandoc


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

# This function creates a search based on the variables above and outputs to a json file. 
def searchToJson():
    today_date = datetime.today().strftime('%Y-%m-%d')
    filename = f"{today_date}.json"
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

def generate_resume_bullets(job_description):
    prompt = f"""
        Here is a resume : {base_resume}
        And here is a job description {job_description}
        I want you find the keywords for experience and technology/skills that are present in the job description and not present in the resume. 
        Take those keywords and rank them in order of importance in relation to the job. 
        Create 1-3 bullets that include as many missing keywords as possible. 
        Rank all the bullets in the resume by relevance to the job. Take the 1-3 bullets that are least relevant and replace 
        the bullets with bullets you've created. 
        Make sure it all blends into the resume in a seamless fashion and output the new resume in the same format. 
    """
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who edits professional resumes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content


# Generate the resume
description = jobDescription('https://www.indeed.com/viewjob?jk=61346edc64651631&from=serp&vjs=3')
resume_text = generate_resume_bullets(description)
print(resume_text)



docx_path = 'Kea Braekman Resume.docx'
pdf_path = 'Kea Braekman Resume.pdf'
output_pdf_path = 'Kea Braekman Resume Updated.pdf'
output_docx_path = 'Kea Braekman Resume Updated.docx'

def update_docx(docx_path, new_text, output_path):
    doc = Document(docx_path)
    for para in doc.paragraphs:
        if 'Booz Allen Hamilton' in para.text:
            para.clear()
            para.add_run(new_text)
            break
    doc.save(output_path)
    
update_docx(docx_path, resume_text, output_docx_path)
# pypandoc.download_pandoc()
pypandoc.convert_file(output_docx_path, 'pdf', outputfile=output_pdf_path)


driver.quit()



# OpenAI will not be able to output a docx or pdf file.
# We have a base resume string with bullets etc, might need to format into string array maybe.
# But the idea is for OpenAI to edit strings and then use python to make those strings into docx or pdf
# And format it correctly. then put it into spreadsheet. 
