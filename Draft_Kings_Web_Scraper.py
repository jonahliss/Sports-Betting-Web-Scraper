import requests
from bs4 import BeautifulSoup
import pandas as pd


def appendDataSpreads(html_list, new_list):
    i = 0
    temp_list = []
    for item in html_list:
        if item.text[0] != "O" and item.text[0] != "U":
            temp_list.append(item.text)
    for item in temp_list:
        if i % 2 == 0:
            new_list.append(item)
        i += 1

        
def appendDataOdds(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)

        
def appendDataTeams(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)
     

class SportStatic:
    def __init__(self, URL):
        self.url = URL
        self.page = ''
        self.soup = ''
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
        self.spreads_html = self.soup.find_all(class_='sportsbook-outcome-body-wrapper')
        self.odds_html = self.soup.find_all(class_='sportsbook-odds american no-margin default-color')
        self.teams_html = self.soup.find_all(class_='event-cell__name-text')
    def sortData(self):
        appendDataSpreads(self.spreads_html, self.spreads)
        appendDataOdds(self.odds_html, self.odds)
        appendDataTeams(self.teams_html, self.teams)
    def presentData(self):
        self.df = pd.DataFrame()
        self.df = pd.concat([self.df, pd.DataFrame({'Teams':self.teams}),pd.DataFrame({'Spreads':self.spreads}),
                            pd.DataFrame({'Odds':self.odds})], axis=1)
        print(self.df)

        
# Draft Kings NFL
NFL = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561")
NFL.retrieveData()
NFL.sortData()
NFL.presentData()

# Draft Kings CFB
CFB = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
CFB.retrieveData()
CFB.sortData()
CFB.presentData()

# Draft Kings NBA
NBA = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
NBA.retrieveData()
NBA.sortData()
NBA.presentData()

# Draft Kings CBB
CBB = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")
CBB.retrieveData()
CBB.sortData()
CBB.presentData()
