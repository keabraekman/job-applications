import requests
from bs4 import BeautifulSoup


# Making a GET request
r = requests.get('https://www.indeed.com/jobs?q=devops+engineer&l=90066&from=searchOnHP&vjk=317ad5cb3dfb70c0')

# check status code for response received
# success code - 200
print(r)

# Parsing the HTML
soup = BeautifulSoup(r.content, 'html.parser')
print(soup.prettify())
