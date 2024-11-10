# job-applications
I am making a repo to help with the job application process : job search, resume edits, and job applying. 


I started applying to jobs but realized I am incredibly slow and unproductive. I spend a huge part of my day dealing with applications. 

The job search is difficult and annoying, but the biggest issue is editing my resume. Each job posting has different tools they require/desire.
I want to make a python script that can help me. Here are my ideas : 
1. Make a script that returns the most appropriate job postings from websites like Linkedin or Indeed. 
The idea would be to make a couple curl commands on the newest job postings, have OpenAI's API review them and rank them by pretinence to my skillset. I still need to become more familiar with OpenAI's API but can definitely be done. I will need to come 
up with a more repeatable framework for this. 
2. Make a script that edits my resume, names it appropriately and outputs a pdf file I can use to apply to that job. 
Maybe make a excel spreadsheet with the jobs I want to apply to. Maybe a script that calls a search, and then one that 
outputs the required resumes. Something like that. 
3. Then, the manual work can be either done by me, or can be outsourced. Really all that's needed is to copy stuff from the resume into the job portal or whatever. Should be pretty trivial. 

Steps : 
1. Make a script that returns a list of best job postings. Let's call it search.py