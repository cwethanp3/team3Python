import random 
class Website:
    
    def __init__(self, URL):
        #TODO: Lookup URL in database
        self.URL = URL

    def getURL(self):
        return self.URL

    def hasChanged(self, HTML):
        #TODO: Make an actual Comparison against the database
        #For now return a random boolean
        return bool(random.getrandbits(1))

    def getEmails(self):
        #TODO: get email list from Database
        return ["mypaiswell@gmail.com", "Fake@epawelski.com"]
