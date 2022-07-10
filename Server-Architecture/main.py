import datetime as dt
import random as rand
import python_weather
import asyncio
import geocoder
import os
import json
from bs4 import BeautifulSoup
import datetime
import csv
#Import cryptography related modules
import base64
from hashlib import sha256
#Import Google related modules
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#Import Web-dev related modules
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import UserMixin
from flask_session import Session

#Initialize Flask web app
app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

#Initialize various random variables
langs = ["English", "Italiano"]
greetings = [[["Good Morning", "Buongiorno"], ["Good Day", "Buongiorno"], ["Good Afternoon", "Buon pomeriggio"], ["Good Evening", "Buona sera"]], [["I'm glad to see that you seem ok", "Mi fa piacere vedere che tu stia bene"], ["It's nice to meet you again", "Mi fa piacere riincontrarti"]]]
weathernames = [
    ["Partly Cloudy", "Parzialmente nuvoloso"],
    ["Partly Sunny", "Parzialmente soleggiato"],
    ["Cloudy", "Nuvoloso"],
    ["Sunny", "Soleggiato"],
    ["Mostly Sunny", "Prevalentemente soleggiato"],
    ["Thunderstorm", "Tempeste di neve"],
    ["Rain Snow", "Neve e pioggia"],
    ["Chance Of Snow", "Possibili nevicate"],
    ["Partly Cloudy", "Parzialmente Nuvoloso"],
    ["Mostly Cloudy", "Prevalentemente nuvoloso"]
]
#The following represents open weather code assigned to various weather configurations
weathercodesop = {
    "Partly Cloudy": "02",
    "Partly Sunny": "02",
    "Cloudy": "03",
    "Sunny": "01",
    "Mostly Cloudy":"03",
    "Mostly Sunny": "01",
    "Thunderstorm": "13",
    "Rain Snow": "09",
    "Chance Of Snow": "13"
}

#Initialize JSON parser for gmail-related credentials
with open('credentials.json') as cred_file:
    cred = json.load(cred_file)
#Initialize Gmail-related things
id = cred['installed']['client_id']
passw = cred['installed']['client_secret']
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#Function to check if a user exists and to find the corrispective folder code
def checkuserlogin(username, password):
    code = False #We use the 'code' variable as a possible flag for failed search of the username
    with open('lookuptable.csv', newline='') as f:
        userlist = list(csv.reader(f))
    for x in range(0, len(userlist)):
        if username in userlist[x]:
            code = userlist[x]
    if code == False:
        return 0
    else:
        with open(str("user/{}/userdata.csv").format(str(code[1])), newline='') as f:
            udata = list(csv.reader(f))
        if udata[1][0] == sha256(password.encode('utf-8')).hexdigest():
            return [2, code]
        else:
            print(udata[1][0])
            print(sha256(password.encode('utf-8')).hexdigest())
            return 3

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
    l = ts+ name + ". \n"+greetings[1][rand.randint(0,1)][lang]
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

def getgooglemails(n, creds, labels):
    try:
        service = build('gmail', 'v1', credentials=creds)
        if labels == False:
            results = service.users().messages().list(maxResults=n, userId='me').execute()
        else:
            results = service.users().messages().list(maxResults=n, userId='me', labelIds=labels).execute()
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
    try:
        parts = payload.get('parts')[0]
    except TypeError:
        return ["There has been a problem parsing the Email", "Please, try again later", ""]
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

def translateweathers(lang, engname):
    for x in weathernames:
        if engname == x[0]:
            return x[lang]
    return engname #This condition implies that no translation was actually found, it's suggested to not trigger an error

def opwiconcalculator(time, weather): #Calculates the correct icon to show in dashboard etc., extracts from openweather website (Thanks openweather!)
    if time < 19:
        timecode="d"
    else:
        timecode="n"
    if weather in weathercodesop:
        return "http://openweathermap.org/img/wn/" + str(weathercodesop[weather]) + str(timecode) + "@2x.png"

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    res = checkuserlogin(username, password)
    if res != 0 and res != 3:
        session['name'] = username
        session['code'] = res[1]
        return redirect(request.url_root)
    else:
        flash('Errore: Email o Password errati')
        return redirect(url_for('login'))

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return(redirect(request.url_root))
@app.route('/')
def main():
    loc = tracedevice()
    asyncioprogr = asyncio.new_event_loop()
    weat = asyncioprogr.run_until_complete(getweather(loc))
    print(loc, weat[1][1], weat[1][2])
    imagelinktemp = opwiconcalculator(datetime.datetime.now().hour, weat[1][1])
    weat[1][1] = translateweathers(1, weat[1][1])
    c = getgooglecredsforgmail(str(44532))
    lis = getgooglemails(1, c, "UNREAD")
    email = readmails(lis, 0, c)
    greeting = greetingstart(1, " " + session['name'] if "name" in session else " utente")
    username = session['name'] if "name" in session else "User"
    date = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template('index.html', loc=str(loc), weather=str(weat[1][1]), temp=weat[1][2], ilink = imagelinktemp, emaildata = email, greet = greeting, username=username,hour = date)
#Inizializza l'applicazione
if __name__ == '__main__':
    app.run()
