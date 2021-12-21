import requests
import gspread
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def getRange(index):
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


# PURPOSE: removes all special chracters from the key
# PURPOSE: makes the key lowercase
def formatKey(key):
    key = key.lower()
    key = key.replace("(", "")
    key = key.replace(")", "")
    key = key.replace(" - ", " ")
    key = key.replace("1h", "1st half")
    key = key.replace("2h", "2nd half")
    key = key.replace("1q", "1st quarter")
    key = key.replace("qtr", "quarter")
    key = key.replace("2q", "2nd quarter")
    key = key.replace("3q", "3rd quarter")
    key = key.replace("4q", "4th quarter")
    key = key.replace("bk", "basketball")
    key = key.replace("b ", "basketball")
    key = key.replace("fb", "football")
    key = key.replace("lines", "")
    return key


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install())


class SportStatic:
    def __init__(self, URL):
        self.url = URL
        self.teams_list = []
        self.spreads_list = []
        self.odds_list = []
        self.moneylines_list = []
        self.df = []
        
    def retrieveData(self):
        driver.get(self.url)
        page = driver.page_source
        self.soup = BeautifulSoup(page, "html.parser")

    def sortData(self):
        for event in self.soup.select('div.parlay-card-10-a'):
            children = event.find_all('tr')
            for child in children[1:]:
                try:
                    team = child.find_all(class_='event-cell__name-text')[0].text
                except:
                    team = "NaN"
                try:
                    moneyline = child.find_all(class_='sportsbook-odds american no-margin default-color')[0].text
                except:
                    moneyline = "NaN"
                try:
                    temp = child.find_all(class_='sportsbook-outcome-body-wrapper')[1].text
                    if (temp == moneyline):
                        odds = "NaN"
                    else:
                        odds = temp
                    spread = child.find_all(class_='sportsbook-outcome-body-wrapper')[0].text
                except:
                    try:
                        temp = child.find_all(class_='sportsbook-outcome-body-wrapper')[0].text 
                        if (temp[0] == 'O' or temp[0] == 'U'):
                            spread = "NaN"
                            odds = temp
                        elif (temp == moneyline):
                            spread = "NaN"
                            odds = "NaN"
                        else:
                            spread = temp
                            odds = "NaN"
                    except:
                        spread = "NaN"
                        odds = "NaN"
                
                '''
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
                '''

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
worksheet = sh.get_worksheet(5)


scraping_list = [['A1','NFL','https://sportsbook.draftkings.com/leagues/football/88670561','B:E'],
                 ['F1','NFL Halves','https://sportsbook.draftkings.com/leagues/football/88670561?category=halves','G:J'],
                 ['K1','CFB','https://sportsbook.draftkings.com/leagues/football/88670775', 'L:O'],
                 ['P1','CFB Halves','https://sportsbook.draftkings.com/leagues/football/88670775?category=halves', 'Q:T'],
                 ['U1','NBA','https://sportsbook.draftkings.com/leagues/basketball/88670846', 'V:Y'],
                 ['Z1','NBA Halves','https://sportsbook.draftkings.com/leagues/basketball/88670846?category=halves', 'AA:AD'],
                 ['AE1','CBB','https://sportsbook.draftkings.com/leagues/basketball/88670771', 'AF:AI'],
                 ['AJ1','CBB Halves','https://sportsbook.draftkings.com/leagues/basketball/88670771?category=halves', 'AK:AN']]

while True:
    
    for item in scraping_list:
        print('Starting', item[1])
        worksheet.update(item[0], item[1])
        obj = SportStatic(item[2])
        obj.collectData()
        df = obj.displayData()
        worksheet.update(item[3], [df.columns.values.tolist()] + df.values.tolist())
        print('Updated', item[1])
