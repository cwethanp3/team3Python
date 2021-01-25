class URL:
    def __init__(self, URL, crawlDepth):
        self.URL = URL
        self.crawlDepth = crawlDepth

    def getURL(self):
        return self.URL

    def getCrawlDepth(self):
        return self.crawlDepth
