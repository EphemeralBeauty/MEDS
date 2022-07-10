import pyttsx3 as ttp
import datetime as dt
import random as rand
import os

langs = ["English", "Italiano"]
greetings = [[["Good Morning", "Buongiorno"], ["Good Day", "Buongiorno"], ["Good Afternoon", "Buon pomeriggio"], ["Good Evening", "Buona sera"]], [["I'm glad to see that you seem ok", "Mi fa piacere vedere che tu stia bene"], ["It's nice to meet you again", "Mi fa piacere riincontrarti"]]]

engine = ttp.init('sapi5')
engine.setProperty('voice', 'voices.id')
#engine.setProperty('rate', 150)

def pronunce(text):
    engine.save_to_file(text, "cdialogue.mp3")
    engine.runAndWait()

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
    pronunce(l)

greetingstart(0, "Uriel")
