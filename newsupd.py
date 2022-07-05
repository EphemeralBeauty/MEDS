from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

defwords = ["esteri", "politica", "economia", "cronaca"]

def getLaRepNewsLinks():
    deflinks = []
    req = Request("https://www.repubblica.it/")
    html_ver=urlopen(req)
    soup = BeautifulSoup(html_ver, "lxml")
    links = []
    for x in soup.findAll('a'):
        links.append(x.get('href'))
    for x in links:
        if str(x).startswith("https://www.repubblica.it/") and x != None and any(el in x for el in defwords):
            for letpos in range(0, len(x)): #Check the condition in a reverse order
                if x[len(x)-letpos-1].isdigit():
                    deflinks.append(str(x))
                    break
    return deflinks

def readLaRepNews(link):
    page = urlopen(link)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    extractedtitle = soup.find_all("h1", {"class" : "story__title"})
    extractedsummary = soup.find_all("div", {"class" : "story__summary"})
    extracteddate = [(soup.find_all("time", {"class" : "story__date"}))[0].get_text(), (soup.find_all("span", {"class" : "story__date__update"}))[0].get_text()]
    extractedtext = []
    for el in soup.find_all("div", {"class" : "story__content"}):
        extractedtext.append(el.get_text())
    return extractedtitle[0].get_text(), extractedsummary[0].get_text(), extracteddate, extractedtext

#print(getLaRepNewsLinks())
#print(readLaRepNews("https://www.repubblica.it/esteri/2022/07/01/diretta/ucraina_russia_news_oggi_guerra-356125355/"))
