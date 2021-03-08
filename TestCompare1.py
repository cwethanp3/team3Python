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

def crawl(URLString, CrawlDepth, WebsiteID):
    #TODO: Handle PDF's
    if(URLString[0:4].upper() == 'HTTP'):
        if(URLString not in HTMLList):
            try:
                response = requests.get(URLString)
                soup = BeautifulSoup(response.content, 'html.parser')
                HTMLList.append(URLString)              
                HTMLDictList.append(dict({"URL":URLString, "HTML": soup.prettify(), "WebsiteID": WebsiteID}))
                print("Saved: " + URLString)
                if (CrawlDepth > 1):
                    for link in BeautifulSoup(response.content,'html.parser', parse_only=SoupStrainer('a')):
                        if link.has_attr('href'):
                            crawl(urljoin(URLString,link['href']), CrawlDepth - 1, WebsiteID)
            #TODO: Allow Keyboard Escape
            except Exception as e:
                print("Unexpected Error on URL: " + URLString + str(e))
    else:
       print("Bad URL: " + URLString)

def sendReport(website, sender):
    emailList = website.getEmails()
    #TODO: make this message user changable
    message = website.getMessage()
    subject = "Changes to " + str(website.getURL())

    for email in emailList:
        #Commented out for testing
        sender.sendFullEmail("me", email, subject, message, website.images)
        print("Email Sent to: " + email)

    website.removeImages()


#Program Mainline

URLObj = URLBuilder()
URLList = URLObj.getURLList()
sender = gmailSender()

URLs = []
URLs.append(URL("https://www.timeanddate.com/worldclock/usa/new-york", 1, 4))


for URLItem in URLs:
    crawl(URLItem.getURL(), URLItem.getCrawlDepth(), URLItem.getWebsite_ID())
    #Crawl builds HTMLDictList
print("Checking...")
for websiteData in HTMLDictList:
    website = Website(websiteData["URL"], websiteData["HTML"], websiteData["WebsiteID"])
    if(website.hasChanged()):
        sendReport(website, sender)
