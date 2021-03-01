from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from base64 import urlsafe_b64encode
import sys
import os.path
import pickle



class gmailSender:
    def __init__(self):

        SCOPE = ['https://www.googleapis.com/auth/gmail.compose'] # Allows sending only, not reading

        # Initialize the object for the Gmail API
        """# https://developers.google.com/gmail/api/quickstart/python
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPE)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))
        """
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if getattr(sys, 'frozen', False):
                   flow = InstalledAppFlow.from_client_secrets_file( os.path.join(sys._MEIPASS, "files/credentials.json"), SCOPE)
                else:
                    #flow = client.flow_from_clientsecrets('client_secret.json', SCOPE)
                    flow = InstalledAppFlow.from_client_secrets_file(
                    'files/credentials.json', SCOPE)
                #print(SCOPE)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)


    # https://developers.google.com/gmail/api/guides/sending
    def create_message(self,sender, to, subject, message_text):
      """Create a message for an email.
      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
      Returns:
        An object containing a base64url encoded email object.
      """
      message = MIMEText(message_text, 'html')
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject
      encoded_message = urlsafe_b64encode(message.as_bytes())
      return {'raw': encoded_message.decode()}


    # https://developers.google.com/gmail/api/guides/sending
    def send_message(self, service, user_id, message):
      """Send an email message.
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.
      Returns:
        Sent Message.
      """
      try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        #print('Message Id: %s' % message['id'])
        return message
      #except errors.HttpError, error:
      except Exception as e:
        print('An error occurred: '+ str(e))

    def sendFullEmail(self, SENDER, RECIPIENT, SUBJECT, CONTENT):
        raw_msg = self.create_message(SENDER, RECIPIENT, SUBJECT, CONTENT)
        self.send_message(self.service, "me", raw_msg)
