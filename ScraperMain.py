import requests
from bs4 import BeautifulSoup

URL = 'https://www.monster.com/jobs/search/?q=Software-Developer&where=Australia'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
#results = soup.find(id='ResultsContainer')
title_elem = soup.find('body')
print(title_elem.prettify())
