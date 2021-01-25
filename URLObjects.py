from URL import URL
class URLBuilder:
    def __init__(self):
        self.URLs = [URL("https://www.ldplanroom.com/jobs/public?status=bidding ", 1),
                     URL("https://www.emmetcrc.org/projects", 1),
                     URL("https://www.bidnetdirect.com/mitn/city-of-hamtramck", 1),
                     URL("https://cityofmidlandmi.gov/bids.aspx", 1),
                     URL("http://eatoncountyroad.com/doing-business-with-us/bid-information",1),
                     URL("https://www.ldplanroom.com/password/forgot",1)]

    def getURLList(self):
        return self.URLs

class URL:
    def __init__(self, URL, crawlDepth):
        self.URL = URL
        self.crawlDepth = crawlDepth

    def getURL(self):
        return self.URL

    def getCrawlDepth(self):
        return self.crawlDepth
