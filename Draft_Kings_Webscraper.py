import requests
from bs4 import BeautifulSoup
import pandas as pd

def appendData(html_list, new_list):
    i = 0
    for item in html_list:
        if i % 2 == 0:
            new_list.append(item.text)
        i += 1
        
def appendDataTeams(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)

class SportStatic:
    def __init__(self, URL, classes):
        self.url = URL
        self.page = ''
        self.soup = ''
        self.classes = classes
        self.spreads_html = []
        self.odds_html = []
        self.teams_html = []
        self.spreads = []
        self.odds = []
        self.teams = []
        self.df = []
    def retrieveData(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.spreads_html = self.soup.find_all(class_=self.classes[0])
        self.odds_html = self.soup.find_all(class_=self.classes[1])
        self.teams_html = self.soup.find_all(class_=self.classes[2])
    def sortData(self):
        appendData(self.spreads_html, self.spreads)
        appendData(self.odds_html, self.odds)
        appendDataTeams(self.teams_html, self.teams)
    def presentData(self):
        self.df = pd.DataFrame()
        self.df = pd.concat([self.df, pd.DataFrame({'Teams':self.teams}),pd.DataFrame({'Spreads':self.spreads}),
                            pd.DataFrame({'Odds':self.odds})], axis=1)
        return self.df
        
draftkings_classes = ['sportsbook-outcome-cell__line','sportsbook-odds american default-color','event-cell__name-text']
        
# Draft Kings NFL
NFL = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561", draftkings_classes)
NFL.retrieveData()
NFL.sortData()
NFL.presentData()

# Draft Kings CFB
CFB = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775", draftkings_classes)
CFB.retrieveData()
CFB.sortData()
CFB.presentData()

# Draft Kings NBA
NBA = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846", draftkings_classes)
NBA.retrieveData()
NBA.sortData()
NBA.presentData()

# Draft Kings CBB
CBB = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771", draftkings_classes)
CBB.retrieveData()
CBB.sortData()
CBB.presentData()
