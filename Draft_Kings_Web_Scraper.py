import time

import requests
import gspread
from bs4 import BeautifulSoup
import pandas as pd


def getRange(index):
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


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
                    team = team.lower()
                    team = team.strip()
                except:
                    team = "NaN"
                try:
                    spread = child.find_all(class_='sportsbook-outcome-body-wrapper')[0].text
                except:
                    spread = "NaN"
                try:
                    odds = child.find_all(class_='sportsbook-outcome-body-wrapper')[1].text
                    odds = odds.replace('O ', 'o')
                    odds = odds.replace('U ', 'u')
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
        

gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")
worksheet = sh.get_worksheet(1)


while True:
    
    NFL = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561")
    NFL.collectData()
    dfNFL = NFL.displayData()
    worksheet.update('B:E', [dfNFL.columns.values.tolist()] + dfNFL.values.tolist())
    print('NFL Updated')
    
    CFB = SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
    CFB.collectData()
    dfCFB = CFB.displayData()
    worksheet.update('G:J', [dfCFB.columns.values.tolist()] + dfCFB.values.tolist())
    print('CFB Updated')
    
    NBA = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
    NBA.collectData()
    dfNBA = NBA.displayData()
    worksheet.update('L:O', [dfNBA.columns.values.tolist()] + dfNBA.values.tolist())
    print('NBA Updated')
    
    CBB = SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")
    CBB.collectData()
    dfCBB = CBB.displayData()
    worksheet.update('Q:T', [dfCBB.columns.values.tolist()] + dfCBB.values.tolist())
    print('CBB Updated')

    time.sleep(10)
