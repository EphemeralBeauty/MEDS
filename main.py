import datetime as dt
import random as rand
import python_weather
import asyncio
import geocoder
import os
import json
from bs4 import BeautifulSoup
import base64
#Import Google related modules
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#Import Web-dev related modules
from flask import Flask, render_template

#Initialize Flask web app
app = Flask(__name__)

#Initialize various random variables
langs = ["English", "Italiano"]
greetings = [[["Good Morning", "Buongiorno"], ["Good Day", "Buongiorno"], ["Good Afternoon", "Buon pomeriggio"], ["Good Evening", "Buona sera"]], [["I'm glad to see that you seem ok", "Mi fa piacere vedere che tu stia bene"], ["It's nice to meet you again", "Mi fa piacere riincontrarti"]]]

#Initialize JSON parser for gmail-related credentials
with open('credentials.json') as cred_file:
    cred = json.load(cred_file)
#Initialize Gmail-related things
id = cred['installed']['client_id']
passw = cred['installed']['client_secret']
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def greetingstart(lang, name):
    hour = dt.datetime.now().hour
    if hour >= 4 and hour < 11:
        ts = greetings[0][0][lang]
    elif hour >= 11 and hour < 15:
        ts = greetings[0][1][lang]
    elif hour >= 15 and hour <= 18:
        ts = greetings[0][2][lang]
    else:
        ts = greetings[0][3][lang]
    l = ts+ name + ". "+greetings[1][rand.randint(0,1)][lang]
    return l

def tracedevice():
    ip = geocoder.ip("me")
    return ip.city

async def getweather(city):
    client = python_weather.Client()
    weather = await client.find(city)
    l = [weather.current.temperature]
    for forecast in weather.forecasts:
        l.append([str(forecast.date), forecast.sky_text, forecast.temperature])
    await client.close()
    return l

def getgooglecredsforgmail(univoch):
    creds = None
    temp = os.path.join('user', univoch)
    if not os.path.exists(temp):
        os.mkdir(temp)
    l = os.path.join('user', univoch, 'token.json')
    if os.path.exists(l):
        creds = Credentials.from_authorized_user_file(l, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(l, 'w') as token:
            token.write(creds.to_json())
    return creds

def getgooglemails(n, creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(maxResults=n, userId='me').execute()
        msg = results.get('messages')
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
    return msg

def readmails(msg, n, creds):
    service = build('gmail', 'v1', credentials=creds)
    proc = msg[n]
    print(proc)
    txt = service.users().messages().get(userId='me', id=proc['id']).execute()
    # Get value of 'payload' from dictionary 'txt'
    payload = txt['payload']
    headers = payload['headers']

    # Look for Subject and Sender Email in the headers
    for d in headers:
        if d['name'] == 'Subject':
            subject = d['value']
        if d['name'] == 'From':
            sender = d['value']

    # The Body of the message is in Encrypted format. So, we have to decode it.
    # Get the data and decode it with base 64 decoder.
    parts = payload.get('parts')[0]
    data = parts['body']['data']
    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)

    # Now, the data obtained is in lxml. So, we will parse
    # it with BeautifulSoup library
    soup = BeautifulSoup(decoded_data , "lxml")
    #soup = BeautifulSoup(decoded_data , "xml")
    body = soup.body()

    # Printing the subject, sender's email and message
    res = [subject, sender, body]
    #print("Subject: ", subject)
    #print("From: ", sender)
    #print("Message: ", body)
    #print('\n')
    return res


#c = getgooglecredsforgmail(str(44532))
#lis = getgooglemails(150, c)
#print(type(lis[0]))
#print(readmails(lis, 0, c))

#loop = asyncio.new_event_loop()
#l = loop.run_until_complete(getweather(tracedevice()))
#print(l)

#Inizializza l'applicazione
if __name__ == '__main__':
    app.run()
