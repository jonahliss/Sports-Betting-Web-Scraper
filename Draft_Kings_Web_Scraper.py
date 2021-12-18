import requests
from bs4 import BeautifulSoup
import pandas as pd


class SportStatic:
    def __init__(self, URL):
        self.url = URL
        self.teams_list = []
        self.spreads_list = []
        self.odds_list = []
        self.moneylines_list = []
        self.df = []

    def retrieveData(self):
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.content, "html.parser")

    def sortData(self):
        for event in self.soup.select('div.parlay-card-10-a'):
            children = event.find_all('tr')
            for child in children[1:]:
                try:
                    team = child.find_all(class_='event-cell__name-text')[0].text
                except:
                    team = "NaN"
                try:
                    spread = child.find_all(class_='sportsbook-outcome-body-wrapper')[0].text
                except:
                    spread = "NaN"
                try:
                    odds = child.find_all(class_='sportsbook-outcome-body-wrapper')[1].text
                except:
                    odds = "NaN"
                try:
                    moneyline = child.find_all(class_='sportsbook-outcome-body-wrapper')[2].text
                except:
                    moneyline = "NaN"

                self.teams_list.append(team)
                self.spreads_list.append(spread)
                self.odds_list.append(odds)
                self.moneylines_list.append(moneyline)

    def displayData(self):
        self.retrieveData()
        self.sortData()
        self.df = pd.DataFrame()
        self.df = pd.concat([self.df, pd.DataFrame({'Team': self.teams_list}), pd.DataFrame({'Spread': self.spreads_list}),
                             pd.DataFrame({'Odds': self.odds_list}), pd.DataFrame({'Moneyline': self.moneylines_list})], axis=1)
        self.df = self.df.fillna('')
        return self.df
    
    def collectData(self):
        self.retrieveData()
        self.sortData()
        
 
NFL = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561")
CFB = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
NBA = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
CBB = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")

while 0 == 0:
    NFL.collectData()
    print(NFL.displayData())
    CFB.collectData()
    print(CFB.displayData())
    NBA.collectData()
    print(NBA.displayData())
    CBB.collectData()
    print(CBB.displayData())
