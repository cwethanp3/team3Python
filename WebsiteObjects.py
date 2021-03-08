import random
import mysql.connector
import difflib
from difflib import Differ
import io
import os
from bs4 import BeautifulSoup, SoupStrainer
from io import StringIO
from io import BytesIO
from BrowserObjects import WebBrowser
import re
from bs4.element import Comment, NavigableString, Tag
from lxml.html.diff import htmldiff
import base64
import time

import warnings
#NOTE: When Compiling uncomment the next line to ignore warnings
warnings.filterwarnings("ignore")

from fuzzywuzzy import fuzz

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


class Website:
    
    def __init__(self, URL, HTML, WebsiteID):
        self.cnx = mysql.connector.connect(user='u498554350_admin', password='^J4wcHr@A',
                              host='141.136.43.1',
                              database='u498554350_TEAM3')
        self.cursor = self.cnx.cursor()
        self.URL = URL
        self.HTML = HTML
        self.WebsiteID = WebsiteID
        self.ChangedText = ""
        self.images = []
        self.words  = []

    def getURL(self):
        return self.URL
    
    def syncHTML(self):
        self.cnx = mysql.connector.connect(user='u498554350_admin', password='^J4wcHr@A',
                              host='141.136.43.1',
                              database='u498554350_TEAM3')
        self.cursor = self.cnx.cursor()

            
        #Save Blob to DB
        query = "SELECT MAX(Blob_ID) FROM BLOBS"
        self.cursor.execute(query)
        BlobID = 1
        for Blob_ID in self.cursor:
          BlobID = (Blob_ID[0] + 1)
        try:
            with io.StringIO() as f:
                f = StringIO(self.HTML)
                query = "INSERT INTO BLOBS (Blob_ID, Blob_Data) VALUES (%s, %s)" 
                args = (BlobID, f.read())
                self.cursor.execute(query, args)
                self.cnx.commit()
        except Exception as e:
            print(query)
            print(str(e))

        #Save URLHistory to DB
        if len(self.ChangedText ) > 255:
            self.ChangedText = self.ChangedText[0:255]
        query = "INSERT INTO URL_HISTORY(URL, Changed_Text, Website_ID, Blob_ID) VALUES (\'%s\',\'%s\',%s,%s)" %(self.URL, self.ChangedText, self.WebsiteID, BlobID)
        try:
            self.cursor.execute(query)
            self.cnx.commit()
        except Exception as e:
            print(query)
            print(str(e))

        #Update Last Crawl Time
        query = "UPDATE WEBSITES SET Last_Crawl_DateTime = CURRENT_TIMESTAMP() WHERE WEBSITES.Website_ID = \'%s\'" %(self.WebsiteID)
        try:
            self.cursor.execute(query)
            self.cnx.commit()
        except Exception as e:
            print(query)
            print(str(e))

        #Get Last HTML Scan From Database
        query = "SELECT Blob_Data FROM `URL_HISTORY` join BLOBS on BLOBS.Blob_ID=URL_HISTORY.Blob_ID where URL = \'%s\' order by DateTime_Created desc LIMIT 1" %(self.URL)
        self.cursor.execute(query)
        self.HTML = "None"
        try:
            HTMLData = self.cursor.fetchone()[0]
            with io.BytesIO() as f:
                f = BytesIO(HTMLData)
                byte_str = f.read()
                self.HTML = byte_str.decode('UTF-8')
                #self.HTML = str(f.read())
                #self.HTML = self.HTML.replace('\\n','\n')
        except Exception as e:
            print(str(e))
            
    def getChangedText(self):
        return self.ChangedText
        

    def hasChanged(self):
        self.images = []
        self.words  = []
        #Get Last HTML Scan From Database
        query = "SELECT Blob_Data FROM `URL_HISTORY` join BLOBS on BLOBS.Blob_ID=URL_HISTORY.Blob_ID where URL = \'%s\' order by DateTime_Created desc LIMIT 1" %(self.URL)
        self.cursor.execute(query)
        self.OldHTML = "None"
        try:
            HTMLData = self.cursor.fetchone()[0]
            with io.BytesIO() as f:
                f = BytesIO(HTMLData)
                byte_str = f.read()
                self.OldHTML = byte_str.decode('UTF-8')
                #self.OldHTML = str(f.read())
                #self.OldHTML = self.OldHTML.replace('\\n','\n')
        except Exception as e:
            print(str(e))
        

        #Check to see what, if any Filter Type Exists
        query = "SELECT Key_Term, Value FROM WEBSITES join FILTERS on WEBSITES.Filter_Group_ID = FILTERS.Filter_Group_ID where WEBSITES.Website_ID = \'%s\'" %(self.WebsiteID)
        self.cursor.execute(query)
        include = []
        exclude = []
        for (Key_Term, Value) in self.cursor:
          if (Key_Term == "INCLUDE"):
              include.append(Value)
          if (Key_Term == "EXCLUDE"):
              exclude.append(Value)

        self.ChangedText = ""
        self.syncHTML()

        #create a list of relavant elements
        soupX = BeautifulSoup(self.OldHTML, 'html.parser')
        soupY = BeautifulSoup(self.HTML, 'html.parser')

        if len(include) == 0:
            includeList = "body"
        else:
            includeList = include[0]

        for item in exclude:
            for i in soupX.select(item):
                i.decompose()
            for j in soupY.select(item):
                j.decompose()

        ListX = []
        for t in soupX.select(includeList):
            for x in t.findChildren(text=True):
                if(type(x) is NavigableString and not str(x).isspace() ):
                    ListX.append(x)
        ListY = []
        for t in soupY.select(includeList):
            for y in t.findChildren(text=True):
                if(type(y) is NavigableString and not str(y).isspace() ):
                    ListY.append(y)

        #Check for chnages and render elements in selenium
        self.ChangedText = ""
        browser = WebBrowser()
        
        self.changes = self.ElmDiff(ListX, ListY)
        if(len(self.changes) != 0):
            browser.startBrowserQuiet()
            for i, change in enumerate(self.changes):
                if change[0] == "Add":
                    if len(self.images) < 10:
                        self.ChangedText = self.ChangedText + change[1]
                        print("Found Change" + change[1])
                        #todo: add chek to see if these parents exist
                        print(self.findCssSelector(change[1].parent.parent.parent))
                        try:
                            idVar = int(time.time() * 1000) 
                            browser.getCSSScreenshotPNG(self.findCssSelector(change[1].parent.parent.parent), self.URL, (str(idVar) + "chg.png"))
                            self.images.append(str(idVar) + "chg.png")
                            cleanr = re.compile('<.*?>')
                            cleantext = re.sub(cleanr, '', change[1])
                            self.words.append(cleantext)
                        except Exception as e:
                            print(str(e))
            browser.closeBrowser()
        
        
        if self.ChangedText != "":
            print("Found Changes on %s" %(self.URL))
    

        return self.ChangedText != ""

    def removeImages(self):
        for image in self.images:
            try:
                os.remove(image)
            except Exception as e:
                    print(str(e))
    
    def findCssSelector(self, tag):
        temptag = tag
        n = 1
        rtn = tag.name
        while (temptag.previous_sibling  != None):
            if (type(temptag.previous_sibling) == Tag):
                n=n+1
            temptag = temptag.previous_sibling
        rtn = rtn + ":nth-child(" + str(n) +")"
        temptag = tag
        while (temptag.parent != None and temptag.parent.name != "[document]"):
            m = 1
            temptagm = temptag.parent
            while (temptagm.previous_sibling  != None):
                if (type(temptagm.previous_sibling) == Tag):
                    m = m+1
                temptagm = temptagm.previous_sibling 
            rtn =  str(temptag.parent.name) + ":nth-child(" + str(m) + ") > " + rtn
            temptag = temptag.parent
        return rtn

    def compareHTML(self, text1, text2):
        print("Loading HTML")
        text1b = text1.lower().split('\n')
        text2b = text2.lower().split('\n')
        output = []

        for i, line1 in enumerate(text1b):
            #print(line1)
            for j, line2 in enumerate(text2b):
                if line1 == line2 :
                    #print("Skipped:" + line2)
                    text2b[:] = [line2 for line2 in text2b if line1 != line2]
                    break
                print("Added" + line2)
                output.append(line2)
        outString = ""
        for item in output:
            outString += (item + '\n')
        print (outString)
        return outString

    def getEmails(self):
        self.cnx = mysql.connector.connect(user='u498554350_admin', password='^J4wcHr@A',
                              host='141.136.43.1',
                              database='u498554350_TEAM3')
        self.cursor = self.cnx.cursor()
        emails = []
        query = "SELECT Email_Address FROM `EMAILS` join EMAIL_GROUPS on EMAILS.Email_ID = EMAIL_GROUPS.Email_ID join WEBSITES on EMAIL_GROUPS.Website_Group_ID=WEBSITES.Website_Group_ID where WEBSITES.Website_ID = \'%s\'" %(self.WebsiteID)
        self.cursor.execute(query)
        for Email_Address in self.cursor:
          emails.append(Email_Address[0])
        return emails
    
    def write_file(self, data, filename):
        with open(filename, 'wb') as f:
            f.write(data)

    def getMessage(self):
        HTML =        "<h1> Changes to " + self.getURL()+ "</h1>"
        HTML = HTML + "<table>"
        for w, image in enumerate(self.images):
            HTML = HTML + "<tr>"
            HTML = HTML + "<th>" + self.words[w] + "</th>"
            HTML = HTML + "<th> <img src=\"cid:image"+ str(w) + "\" alt=\"HTML Element\" />"
            HTML = HTML + "</th>"
            HTML = HTML + "</tr>"
            
        HTML = HTML + "</table>"
        text_file = open("sample.html", "w")
        n = text_file.write(HTML)
        text_file.close()
        return HTML
            



        
    def read_blob(self):
        # select photo column of a specific author
        query = "SELECT photo FROM authors WHERE id = %s"

        # read database configuration
        db_config = read_db_config()

        try:
            # query blob data form the authors table
            conn = MySQLConnection(**db_config)
            cursor = conn.cursor()
            cursor.execute(query, (author_id,))
            photo = cursor.fetchone()[0]

            # write blob data into a file
            write_file(photo, filename)

        except Error as e:
            print(e)

        finally:
            cursor.close()
            conn.close()

    def ElmDiff(self, listX, listY):
        rtn = []
        lookup = [[0 for x in range(len(listY) + 1)] for y in range(len(listX) + 1)]
        self.LCSLength(listX, listY, len(listX), len(listY), lookup)
        self.ElmDiffRecursive(listX, listY, len(listX), len(listY), lookup, rtn)
        return rtn
        
    def LCSLength(self, X, Y, m, n, lookup):
        # first column of the lookup table will be all 0
        for i in range(m + 1):
            lookup[i][0] = 0
     
        # first row of the lookup table will be all 0
        for j in range(n + 1):
            lookup[0][j] = 0
     
        # fill the lookup table in a bottom-up manner
        for i in range(1, m + 1):
     
            for j in range(1, n + 1):
                # if current character of `X` and `Y` matches
                if str(X[i - 1]) == str(Y[j - 1]):
                    lookup[i][j] = lookup[i - 1][j - 1] + 1
                    # otherwise, if the current character of `X` and `Y` don't match
                else:
                    lookup[i][j] = max(lookup[i - 1][j], lookup[i][j - 1])


    def ElmDiffRecursive(self, X, Y, m, n, lookup, rtn):
        # if the last element of `X` and `Y` matches
        if m > 0 and n > 0 and str(X[m - 1]).strip() == str(Y[n - 1]).strip():
            self.ElmDiffRecursive(X, Y, m - 1, n - 1, lookup, rtn)
            #print("", str(X[m - 1]), end='')
     
        # if the current element of `Y` is not present in `X`
        elif n > 0 and (m == 0 or lookup[m][n - 1] >= lookup[m - 1][n]):
            self.ElmDiffRecursive(X, Y, m, n - 1, lookup, rtn)
            rtn.append(["Add", Y[n - 1]])
            #print(" +" + str(Y[n - 1]), end='')
     
        # if the current element of `X` is not present in `Y`
        elif m > 0 and (n == 0 or lookup[m][n - 1] < lookup[m - 1][n]):
            self.ElmDiffRecursive(X, Y, m - 1, n, lookup, rtn)
            rtn.append(["Rmv", Y[n - 1]])
            #print(" -" + str(X[m - 1]), end='')
