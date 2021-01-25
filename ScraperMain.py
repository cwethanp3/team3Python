import requests
from URLObjects import URLBuilder, URL
from WebsiteObjects import Website
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
from sendEmail import gmailSender

#Global Variables (Yikes!!)
#TODO: save the HTML into the database, if we keep in memory we may run out
HTMLDictList = []
HTMLList = []

def crawl(URLString, CrawlDepth):
    #TODO: Handle PDF's
    if(URLString[0:4].upper() == 'HTTP'):
        if(URLString not in HTMLList):
            try:
                response = requests.get(URLString)
                soup = BeautifulSoup(response.content, 'html.parser')
                HTMLList.append(URLString)
                HTMLDictList.append(dict({"URL":URLString, "HTML": soup.prettify()}))
                print("Saved: " + URLString)
                if (CrawlDepth > 1):
                    for link in BeautifulSoup(response.content,'html.parser', parse_only=SoupStrainer('a')):
                        if link.has_attr('href'):
                            crawl(urljoin(URLString,link['href']), CrawlDepth - 1)
            #TODO: Allow Keyboard Escape
            except:
                print("Unexpected Error on URL: " + URLString)
    else:
       print("Bad URL: " + URLString)

def sendReport(website):
    emailList = website.getEmails()
    #TODO: make this message user changable
    message = "Attention: The following website has changed: " + str(website.getURL())
    sender = gmailSender()
    for email in emailList:
        sender.sendFullEmail("me", email, "Test2", message)
        print("Email Sent to: " + email)


#Program Mainline
URLObj = URLBuilder()
URLList = URLObj.getURLList()

for URLItem in URLList:
    crawl(URLItem.getURL(), URLItem.getCrawlDepth())
    #Crawl builds HTMLDictList
for websiteData in HTMLDictList:
    website = Website(websiteData["URL"])
    if(website.hasChanged(websiteData["HTML"])):
        sendReport(website)
