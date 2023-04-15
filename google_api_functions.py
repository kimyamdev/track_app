from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#from google.oauth2.service_account import Credentials
import googleapiclient.discovery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json, base64
import pickle
import os
import pandas as pd


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'app_key.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def get_spreadsheet_data_into_a_df(spreadsheet_url, sheet_name):

    service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)
    # Get the spreadsheet ID from the URL
    spreadsheet_id = spreadsheet_url.split('/')[-2]
    # Get the data from the first sheet
    sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    # Convert the data to a Pandas DataFrame
    values = sheet.get('values', [])
    print(values[1:])
    print(values[0])
    df = pd.DataFrame(values[1:], columns=values[0])
    print("TX DF FROM GOOGLE SPREADSHEET")
    print(df)
    return df

def send_email(to, subject, body, image_path):
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Create a multipart message container and set the subject and recipient
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # Add the body of the message
        message.attach(MIMEText(body, 'html'))

        # Open the image file and attach it to the message
        with open(image_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<image1>')
            message.attach(img)

        # Create the message and send it
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()

        print(F'sent message to {to} Message Id: {send_message["id"]}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message


