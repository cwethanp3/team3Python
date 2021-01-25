from URL import URL
class URLHandler:
    def __init__(self):
        self.URLs = [URL("https://www.ldplanroom.com/jobs/public?status=bidding ", 1),
                     URL("https://www.emmetcrc.org/projects", 1),
                     URL("https://www.bidnetdirect.com/mitn/city-of-hamtramck", 1),
                     URL("https://cityofmidlandmi.gov/bids.aspx", 1),
                     URL("http://eatoncountyroad.com/doing-business-with-us/bid-information",1)]

    def getURLList(self):
        return self.URLs
