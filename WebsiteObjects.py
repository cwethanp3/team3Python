import random
import mysql.connector
import difflib
from difflib import Differ
import io
from bs4 import BeautifulSoup, SoupStrainer
from io import StringIO
from io import BytesIO
import re
from bs4.element import Comment

from lxml.html.diff import htmldiff

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
                self.HTML = str(f.read())
                self.HTML = self.HTML.replace('\\n','\n')
        except Exception as e:
            print(str(e))
            
    def getChangedText(self):
        return self.ChangedText
        

    def hasChanged(self):
        #Get Last HTML Scan From Database
        query = "SELECT Blob_Data FROM `URL_HISTORY` join BLOBS on BLOBS.Blob_ID=URL_HISTORY.Blob_ID where URL = \'%s\' order by DateTime_Created desc LIMIT 1" %(self.URL)
        self.cursor.execute(query)
        self.OldHTML = "None"
        try:
            HTMLData = self.cursor.fetchone()[0]
            with io.BytesIO() as f:
                f = BytesIO(HTMLData)
                self.OldHTML = str(f.read())
                self.OldHTML = self.OldHTML.replace('\\n','\n')
        except Exception as e:
            print(str(e))
        

        #Check to see what, if any Filter Type Exists
        query = "SELECT type FROM `FILTER_GROUPS` join WEBSITES on WEBSITES.Filter_Group_ID = FILTER_GROUPS.Filter_Group_ID where WEBSITES.Website_ID = \'%s\'" %(self.WebsiteID)
        self.cursor.execute(query)
        self.FilterType = "None"
        for Email_Address in self.cursor:
          self.FilterType = Email_Address[0]

        self.ChangedText = ""
        #Perform the Compare, based on filter type
        self.syncHTML()
        differ = Differ()
        if self.FilterType == "WHT":
            #WHT
            print("")
        else:
            if self.FilterType == "BLK":
                #BLK
                print("")
            else:
                if self.FilterType == "KEY":
                    #KEY
                    print("")
                else:


                    #get visible Text
                    soup1 = BeautifulSoup(self.OldHTML, 'html.parser')
                    soup2 = BeautifulSoup(self.HTML, 'html.parser')
                    [s.extract() for s in soup1(['style', 'script', '[document]', 'head', 'title'])]
                    [s.extract() for s in soup2(['style', 'script', '[document]', 'head', 'title'])]
                    text1b = soup1.getText().lower().split('\n')
                    text2b = soup2.getText().lower().split('\n')
                    text1b = list(filter(lambda a: bool(re.search(' *', a)), text1b))
                    text1b = list(filter(None, text1b))
                    text2b = list(filter(lambda a: bool(re.search(' *', a)), text2b))
                    text2b = list(filter(None, text2b))

                    #Compare two versions
                    self.FuzzRatio = fuzz.ratio(self.OldHTML.lower(), self.HTML.lower())
                    for text in differ.compare(text1b, text2b):
                        if not text.startswith("  ") and not text.startswith("? "):
                            self.ChangedText += text
                            print(text[0:100])
        
        if self.ChangedText != "":
            print("Found Changes on %s, the two versions are %s%% similar" %(self.URL, self.FuzzRatio))
    

        return self.ChangedText != ""

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
        emails = []
        query = "SELECT Email_Address FROM `EMAILS` join EMAIL_GROUPS on EMAILS.Email_Group_ID = EMAIL_GROUPS.Email_Group_ID join WEBSITES on EMAIL_GROUPS.Email_Group_ID=WEBSITES.Email_Group_ID where WEBSITES.Website_ID = \'%s\'" %(self.WebsiteID)
        self.cursor.execute(query)
        for Email_Address in self.cursor:
          emails.append(Email_Address[0])
        return emails
    
    def write_file(self, data, filename):
        with open(filename, 'wb') as f:
            f.write(data)
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
