import requests
import gspread
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Function to standardize text formatting across websites
def formatKey(key):
    key = key.lower()
    key = key.replace("quarters", "1q")
    key = key.replace("quarter", "q")
    key = key.replace("qtr", "q")
    key = key.replace("half", "h")
    key = key.replace("1st", "1")
    key = key.replace("first", "1")
    key = key.replace("2nd", "2")
    key = key.replace("3rd", "3")
    key = key.replace("4th", "4")
    key = key.replace("ncaa basketball", "ncaab")
    key = key.replace("ncaa football", "ncaaf")
    key = key.replace("college football", "ncaaf")
    key = key.replace("margin of victory", "mov")
    key = key.replace("winning margin", "mov")
    key = key.replace("scoring play", "sp")
    key = key.replace("points", "p")
    key = key.replace("basketball", "b")
    key = key.replace("football", "f")
    key = key.replace("@", "vs")
    key = key.replace("2021", "")
    key = key.replace("2022", "")
    key = key.replace("the ", "")
    key = key.replace("(", "")
    key = key.replace(")", "")
    key = key.replace("-", "")
    key = key.replace(" ", "")
    key = key.replace("lines", "")
    key = key.replace("nan", "NaN")
    return key


# Function to classify HTML class text as a team's name, spread, odds, or moneyline
def determineChild(child):
    global teamName, spread, odds, moneyline
    teamName, spread, odds, moneyline = 'NaN', 'NaN', 'NaN', 'NaN'
    try:
        teamName = child.find_all(class_='event-cell__name-text')[0].text
    except:
        pass
    for i in range(3):
        try:
            temp = child.find_all(class_='sportsbook-outcome-body-wrapper')[i].text
            if 'O' in temp or 'U' in temp:
                odds = temp
            elif (temp.count('+') + temp.count('-')) == 2:
                spread = temp
            elif (temp.count('+') + temp.count('-')) == 1:
                moneyline = temp
        except:
            pass
    return teamName, spread, odds, moneyline


# Class to retrieve, sort, and return website data
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
                determineChild(child)
                self.teams_list.append(formatKey(teamName))
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

    
# Launching automated Chrome Browser
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install())


# Establishing connection with Google Sheets
gc = gspread.service_account(filename='credentials.json')
sh = gc.open("BettingScraper")


# Initializing data used to execute scraping process
scraping_list_NFL = [[4,'A1','nfl','football/88670561','B:E'],
                 [4,'F1','nfl1h','football/88670561?category=halves&subcategory=1st-half','G:J'],
                 [4,'K1','nfl2h','football/88670561?category=halves&subcategory=2nd-half','L:O'],
                 [4,'P1','nfl1q','football/88670561?category=quarters&subcategory=1st-quarter','Q:T'],
                 [4,'U1','nfl2q','football/88670561?category=quarters&subcategory=2nd-quarter','V:Y'],
                 [4,'Z1','nfl3q','football/88670561?category=quarters&subcategory=3rd-quarter','AA:AD'],
                 [4,'AE1','nfl4q','football/88670561?category=quarters&subcategory=4th-quarter','AF:AI']]
                 
scraping_list_CFB = [[3,'A1','ncaaf','football/88670775','B:E'],
                 [3,'F1','ncaaf1h','football/88670775?category=halves&subcategory=1st-half','G:J'],
                 [3,'K1','ncaaf2h','football/88670775?category=halves&subcategory=2nd-half','L:O'],
                 [3,'P1','ncaaf1q','football/88670775?category=quarters&subcategory=1st-quarter','Q:T'],
                 [3,'U1','ncaaf2q','football/88670775?category=quarters&subcategory=2nd-quarter','V:Y'],
                 [3,'Z1','ncaaf3q','football/88670775?category=quarters&subcategory=3rd-quarter','AA:AD'],
                 [3,'AE1','ncaaf4q','football/88670775?category=quarters&subcategory=4th-quarter','AF:AI']]
                 
scraping_list_NBA = [[2,'A1','nba','basketball/88670846','B:E'],
                 [2,'F1','nba1h','basketball/88670846?category=halves&subcategory=1st-half','G:J'],
                 [2,'K1','nba2h','basketball/88670846?category=halves&subcategory=2nd-half','L:O'],
                 [2,'P1','nba1q','basketball/88670846?category=quarters&subcategory=1st-quarter','Q:T'],
                 [2,'U1','nba2q','basketball/88670846?category=quarters&subcategory=2nd-quarter','V:Y'],
                 [2,'Z1','nba3q','basketball/88670846?category=quarters&subcategory=3rd-quarter','AA:AD'],
                 [2,'AE1','nba4q','basketball/88670846?category=quarters&subcategory=4th-quarter','AF:AI']]
                 
scraping_list_CBB = [[1,'A1','ncaab','basketball/88670771','B:E',1],
                 [1,'F1','ncaab1h','basketball/88670771?category=halves&subcategory=1st-half','G:J'],
                 [1,'K1','ncaab2h','basketball/88670771?category=halves&subcategory=2nd-half','L:O'],
                 [1,'P1','ncaab1q','basketball/88670771?category=quarters&subcategory=1st-quarter','Q:T'],
                 [1,'U1','ncaab2q','basketball/88670771?category=quarters&subcategory=2nd-quarter','V:Y'],
                 [1,'Z1','ncaab3q','basketball/88670771?category=quarters&subcategory=3rd-quarter','AA:AD'],
                 [1,'AE1','ncaab4q','basketball/88670771?category=quarters&subcategory=4th-quarter','AF:AI']]


# Determining sports and leageus to scrape
options = input('CBB, NBA, CFB, NFL\nWhat data do you want to scrape? ')
scraping_list = []
if 'CBB' in options:
    scraping_list += scraping_list_CBB
if 'NBA' in options:
    scraping_list += scraping_list_NBA
if 'CFB' in options:
    scraping_list += scraping_list_CFB
if 'NFL' in options:
    scraping_list += scraping_list_NFL
    

# Executing scraping process
while True:
    for item in scraping_list:
    # Select Appropriate Spreadsheet
        worksheet = sh.get_worksheet(item[0])
    # Write Title onto Spreadsheet
        print('Starting', item[2])
        worksheet.update(item[1], item[2])
    # Collect Data for Title 
        obj = SportStatic('https://sportsbook.draftkings.com/leagues/'+item[3])
        df = obj.displayData()
    # Insert Data into Spreadsheet
        worksheet.update(item[4], [df.columns.values.tolist()] + df.values.tolist())
        print('Updated', item[2])
