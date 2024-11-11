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
A. ▪ Full Services Team - Hybrid Legacy Application Migration to AWS.
1. o Increased scalability and reliability of 6+ applications by 40%, migrating
hybrid infrastructure to AWS ECS, ECR, RDS, and MQ with Terraform.
2. o Reduced end-to-end application deployment time and manual steps by 50% using
Gitlab CI, Docker, and Terraform.
3. o Integrated Artifactory with AWS ECR for container image storage, simplifying
artifact management and versioning for 20+ Dockerized applications.
B. ▪ Security Services Team - Deployed and Maintained Security Infrastructure.
4. o Deployed and maintained Tenable SC and Trend Micro across 10+ multi-region AWS
accounts, significantly decreased vulnerabilities by automating security scans.
5. o Improved the patching process for security assets which saved 5 hours a week by
automating updates using AWS Inspector, Lambda, and Step Functions.
Software Engineer | Dec. 2020 – Sept. 2022
C. ▪ Foundational Services Team
6. o Automated TLS certificate creation by developing a Gitlab CI pipeline leveraging
AWS ACM across 50+ instances.
D. ▪ Systems Engineer | Aug. 2020 - Dec. 2020
7. o Developed a web scraping Python bot that saved 160+ hours of manual data entry
by curling client financial data into an Excel spreadsheet.
8. o Researched and drafted proposals for Cloud Engineering and FedRAMP projects for
the Department of Defense.
"""

def generate_resume_bullets(job_description):
    prompt = f"""
        Here is a partial resume with numbered bullet points : {base_resume}
        And here is a job description {job_description}
        
        STEP 1 (do not output anything) : 
        Find the keywords for experience/technology/skills that are present in the job description and not present in 
        the resume. If none, output 'NO CHANGES'.

        STEP 2 (do not output anything):
        Take the keywords from step 1 and rank them in order of importance in relation to the job. 

        STEP 3 (do not output anything):
        Create 1-3 bullets: 
        - Write in a consice and precise manner. How an autistic engineer would write it, minimize fluff.
        - Include as many missing keywords as possible in each bullet.
        - Make sure each bullet is formatted like the bullets in the resume (in one cohesive manner) : 
            'Improved X by Y through implementation of Z.'
        - Use arbitrary metrics that sound very impressive : Accomplishments, Percentages, milestones, requests etc...
        
        STEP 4 (do not output anything):
        Find which Section (labeled A-D) is most relevant for each bullet you've created.

        STEP 5 (do not output anything):
        Within each Section (from step 4), save the bullet number(s) that is/are least relevant to the job.
        Each new created bullet must have a unique bullet number it is replacing.
        Add that number at the end of the new bullets you've created (in step 3). Just the number. No 'Replaces bullet'.
        Remove any number at the start of the bullet output. Only keep the sentence:
        For example : 
        Increased scalability and reliability of 6+ applications by 40%, migrating hybrid infrastructure to AWS ECS, ECR, RDS, and MQ with Terraform. 1

        STEP 6 (output something):
        Output each bullet from step 5.

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
# description = jobDescription('https://www.indeed.com/viewjob?jk=61346edc64651631&from=serp&vjs=3')
description = jobDescription('https://www.indeed.com/viewjob?jk=85f378505d17dd50&from=serp&vjs=3')
resume_text = generate_resume_bullets(description)
# print(resume_text)



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


# We get an output of a couple bullet points with numbers. Now we want to replace the original bullets with the new ones
# Bullet numbers will need to be hardcoded. 


# This function will take the GPT output and return a string of only the bullets
def isolateBullets(GPTOutput):
    start_index = GPTOutput.find("STEP 6:")
    if start_index != -1:
        result = GPTOutput[start_index + len("STEP 6:"):].strip()
        return result
    else:
        print("STEP 6: not found in the input.")
        return 'ERROR'

# This function takes the new created bullets in their imperfect format and replaces the bullets in the resume. 
# First we need an index or a way to clear the appropriate bullets. 


# From the gpt output, we create a dictonary where key = bullet to replace and value = new bullet. 
def parse_string_to_dict(input_string):
    lines = input_string.splitlines()
    result_dict = {}
    for line in lines:
        # Split each line by the last space to separate the text from the index
        *text, index = line.rsplit(" ", 1)
        result_dict[int(index)] = " ".join(text)
    return result_dict


resume_text_bullets = isolateBullets(resume_text)
print('resume_text_bullets = ', resume_text_bullets)
print(parse_string_to_dict(resume_text_bullets))



def replaceBullets(doc_path, new_text):
    # Load the document
    doc = Document(doc_path)
    # Define the bullet points by number in a dictionary
    bullet_points = {
        1: 'Increased scalability and reliability of 6+ applications by 40%, migrating hybrid infrastructure to AWS ECS, ECR, RDS, and MQ with Terraform.',
        2: 'Reduced end-to-end application deployment time and manual steps by 50% using Gitlab CI, Docker, and Terraform.',
        3: 'Integrated Artifactory with AWS ECR for container image storage, simplifying artifact management and versioning for 20+ Dockerized applications.',
        4: 'Deployed and maintained Tenable SC and Trend Micro across 10+ multi-region AWS accounts, significantly decreased vulnerabilities by automating security scans.',
        5: 'Improved the patching process for security assets which saved 5 hours a week by automating updates using AWS Inspector, Lambda, and Step Functions.',
        6: 'Automated TLS certificate creation by developing a Gitlab CI pipeline leveraging AWS ACM across 50+ instances.',
        7: 'Developed a web scraping Python bot that saved 160+ hours of manual data entry by curling client financial data into an Excel spreadsheet.',
        8: 'Researched and drafted proposals for Cloud Engineering and FedRAMP projects for the Department of Defense.'
    }
    bullet_numbers = []


    # Find the paragraph that contains the bullet point
    for para in doc.paragraphs:
        if para.text.strip() == bullet_points.get(bullet_number, ""):
            para.text = new_text  # Replace with the new text
            break  # Stop after finding the correct bullet point
    
    # Save the document with a new name or overwrite the original
    doc.save("Updated_" + doc_path)


# def update_docx(docx_path, new_text, output_path):
#     doc = Document(docx_path)
#     for para in doc.paragraphs:
#         if 'Booz Allen Hamilton' in para.text:
#             para.clear()
#             para.add_run(new_text)
#             break
#     doc.save(output_path)




driver.quit()



# OpenAI will not be able to output a docx or pdf file.
# We have a base resume string with bullets etc, might need to format into string array maybe.
# But the idea is for OpenAI to edit strings and then use python to make those strings into docx or pdf
# And format it correctly. then put it into spreadsheet. 
