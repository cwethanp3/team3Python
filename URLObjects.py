import mysql.connector
class URLBuilder:
    def __init__(self):
        self.URLs = []

    def getURLList(self):
        cnx = mysql.connector.connect(user='u498554350_admin', password='^J4wcHr@A',
                              host='141.136.43.1',
                              database='u498554350_TEAM3')
        cursor = cnx.cursor()
        query = ("SELECT Url, Crawl_Depth, Website_ID from `WEBSITES` where round(TIME_TO_SEC(TIMEDIFF(CURRENT_TIMESTAMP, Last_Crawl_DateTime))/60) > Schedule_Interval_Mins")
        cursor.execute(query)

        for (Url, Crawl_Depth, Website_ID) in cursor:
          self.URLs.append(URL(Url, Crawl_Depth, Website_ID))
  
        return self.URLs


class URL:
    def __init__(self, URL, crawlDepth, Website_ID):
        self.URL = URL
        self.crawlDepth = crawlDepth
        self.Website_ID = Website_ID

    def getURL(self):
        return self.URL

    def getCrawlDepth(self):
        return self.crawlDepth

    def getWebsite_ID(self):
        return self.Website_ID
