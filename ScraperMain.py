import requests
from URLHandler import URLHandler
from URL import URL
from bs4 import BeautifulSoup, SoupStrainer

def crawl(URLString, CrawlDepth):
    #TODO: Handle Errors
    response = requests.get(URLString)
    soup = BeautifulSoup(response.content, 'html.parser')
    #TODO: actually save HTML
    print("Pretend I'm saving.. " + soup.prettify()[1:100])
    if (CrawlDepth != 1):
        for link in BeautifulSoup(response.content,'html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                crawl(link['href'], CrawlDepth - 1)
                
URLObj = URLHandler()
URLList = URLObj.getURLList()

for URLItem in URLList:
    crawl(URLItem.getURL(), URLItem.getCrawlDepth()
