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
    key = key.replace("fb", "football")
    key = key.replace("lines", "")
    key = key.replace("o\xa0", "o")
    key = key.replace("u\xa0", "u")
    key = key.replace("nan", "NaN")
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
            
            teamName = "NaN"
            spread = "NaN"
            odds = "NaN"
            moneyline = "NaN"
            
            for child in children[1:]:
                try:
                    team = child.find_all(class_='event-cell__name-text')[0].text
                except:
                    pass
                for i in range(3):
                    try:
                        temp = child.find_all(class_='sportsbook-outcome-body-wrapper')[i].text
                        
                        if 'O' in temp or 'U' in temp:
                            odds = temp
                            odds = odds.replace("½", ".5")
                        elif (temp.count('+') + temp.count('-')) == 2:
                            spread = temp
                        elif (temp.count('+') + temp.count('-')) == 1:
                            moneyline = temp
                    except:
                        pass
            
                self.teams_list.append(formatKey(team))
                self.spreads_list.append(formatKey(spread))
                self.odds_list.append(formatKey(odds))
                self.moneylines_list.append(formatKey(moneyline))

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
        
#%%
gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")


scraping_list = [['A1','nfl','football/88670561','B:E',4],
                 ['F1','nfl 1st half','football/88670561?category=halves&subcategory=1st-half','G:J',4],
                 ['K1','nfl 2nd half','football/88670561?category=halves&subcategory=2nd-half','L:O',4],
                 ['P1','nfl 1st quarter','football/88670561?category=quarters&subcategory=1st-quarter','Q:T',4],
                 ['U1','nfl 2nd quarter','football/88670561?category=quarters&subcategory=2nd-quarter','V:Y',4],
                 ['Z1','nfl 3rd quarter','football/88670561?category=quarters&subcategory=3rd-quarter','AA:AD',4],
                 ['AE1','nfl 4th quarter','football/88670561?category=quarters&subcategory=4th-quarter','AF:AI',4],
                 
                 ['A1','ncaa football','football/88670775','B:E',3],
                 ['F1','ncaa football 1st half','football/88670775?category=halves&subcategory=1st-half','G:J',3],
                 ['K1','ncaa football 2nd half','football/88670775?category=halves&subcategory=2nd-half','L:O',3],
                 ['P1','ncaa football 1st quarter','football/88670775?category=quarters&subcategory=1st-quarter','Q:T',3],
                 ['U1','ncaa football 2nd quarter','football/88670775?category=quarters&subcategory=2nd-quarter','V:Y',3],
                 ['Z1','ncaa football 3rd quarter','football/88670775?category=quarters&subcategory=3rd-quarter','AA:AD',3],
                 ['AE1','ncaa football 4th quarter','football/88670775?category=quarters&subcategory=4th-quarter','AF:AI',3],
                 
                 ['A1','nba','basketball/88670846','B:E',2],
                 ['F1','nba 1st half','basketball/88670846?category=halves&subcategory=1st-half','G:J',2],
                 ['K1','nba 2nd half','basketball/88670846?category=halves&subcategory=2nd-half','L:O',2],
                 ['P1','nba 1st quarter','basketball/88670846?category=quarters&subcategory=1st-quarter','Q:T',2],
                 ['U1','nba 2nd quarter','basketball/88670846?category=quarters&subcategory=2nd-quarter','V:Y',2],
                 ['Z1','nba 3rd quarter','basketball/88670846?category=quarters&subcategory=3rd-quarter','AA:AD',2],
                 ['AE1','nba 4th quarter','basketball/88670846?category=quarters&subcategory=4th-quarter','AF:AI',2],
                 
                 ['A1','ncaa basketball','basketball/88670771','B:E',1],
                 ['F1','ncaa basketball 1st half','basketball/88670771?category=halves&subcategory=1st-half','G:J',1],
                 ['K1','ncaa basketball 2nd half','basketball/88670771?category=halves&subcategory=2nd-half','L:O',1],
                 ['P1','ncaa basketball 1st quarter','basketball/88670771?category=quarters&subcategory=1st-quarter','Q:T',1],
                 ['U1','ncaa basketball 2nd quarter','basketball/88670771?category=quarters&subcategory=2nd-quarter','V:Y',1],
                 ['Z1','ncaa basketball 3rd quarter','basketball/88670771?category=quarters&subcategory=3rd-quarter','AA:AD',1],
                 ['AE1','ncaa basketball 4th quarter','basketball/88670771?category=quarters&subcategory=4th-quarter','AF:AI',1]]


while True:
    for item in scraping_list:
    # Select Appropriate Spreadsheet
        worksheet = sh.get_worksheet(item[4])
    # Write Title onto Spreadsheet
        print('Starting', item[1])
        worksheet.update(item[0], item[1])
    # Collect Data for Title 
        obj = SportStatic('https://sportsbook.draftkings.com/leagues/'+item[2])
        obj.collectData()
        df = obj.displayData()
    # Insert Data into Spreadsheet
        worksheet.update(item[3], [df.columns.values.tolist()] + df.values.tolist())
        print('Updated', item[1])
