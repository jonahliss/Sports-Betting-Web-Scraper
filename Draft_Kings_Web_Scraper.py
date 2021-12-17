import requests
from bs4 import BeautifulSoup
import pandas as pd


def appendDataGeneral(html_list, new_list, iterative):
    i = iterative
    for item in html_list:
        if i % 3 == 0:
            new_list.append(item.text)
        i += 1
        

def appendDataTeams(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)
        

class SportStatic:
    def __init__(self, URL):
        self.url = URL
        self.spreads_html = []
        self.odds_html = []
        self.moneylines_html = []
        self.teams_html = []
        self.spreads = []
        self.odds = []
        self.moneylines = []
        self.teams = []
        self.df = []

    def retrieveData(self):
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.content, "html.parser")
        self.data_html = self.soup.find_all(class_='sportsbook-outcome-body-wrapper')
        self.teams_html = self.soup.find_all(class_='event-cell__name-text')

    def sortData(self):
        appendDataGeneral(self.data_html, self.spreads, 0)
        appendDataGeneral(self.data_html, self.odds, 2)
        appendDataGeneral(self.data_html, self.moneylines, 1)
        appendDataTeams(self.teams_html, self.teams)

    def displayData(self):
        self.retrieveData()
        self.sortData()
        self.df = pd.DataFrame()
        self.df = pd.concat([self.df, pd.DataFrame({'Team': self.teams}), pd.DataFrame({'Spread': self.spreads}),
                             pd.DataFrame({'Odds': self.odds}), pd.DataFrame({'Moneyline': self.moneylines})], axis=1)
        self.df = self.df.fillna('')
        return self.df
    
    def presentData(self):
        self.retrieveData()
        self.sortData()
        self.displayData()


'''
# Draft Kings NFL
NFL = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
NFL.presentData()

# Draft Kings CFB
CFB = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
CFB.presentData()

# Draft Kings NBA
NBA = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
NBA.presentData()

# Draft Kings CBB
CBB = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")
CBB.presentData()
'''
