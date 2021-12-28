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


def formatTeamName(name):
    dictNames = {
        'ohio state': 'ohiostate',
        'michigan state': 'michiganstate',
        'penn state': 'pennstate',
        'texas a&m': 'texasanm',
        'western michigan': 'westernmichigan',
        'air force': 'airforce',
        'mississippi state': 'mississippistate',
        'ole miss': 'mississippi',
        'south carolina': 'southcarolina',
        'iowa state': 'iowastate',
        'oklahoma state': 'oklahomastate',
        'kansas state': 'kansasstate',
        'texas tech': 'texastech',
        'west virginia': 'westvirginia',
        'notre dame': 'notredame',
        'florida state': 'floridastate',
        'georgia tech': 'georgiatech',
        'north carolina state': 'ncstate',
        'north carolina': 'northcarolina',
        'virginia tech': 'virginiatech',
        'boston college': 'bostoncollege',
        'wake forest': 'wakeforest',
        'washington state': 'washingtonstate',
        'oregon state': 'oregonstate',
        'arizona state': 'arizonastate',
        'central michigan': 'centralmichigan',
        'eastern michigan': 'easternmichigan',
        'central florida': 'centralflorida',
        'miami (oh)': 'miamiohio',
        'western kentucky': 'westernkentucky',
        'boise state': 'boisestate',
        'fresno state': 'fresnostate',
        'wichita state': 'wichita',
        'seton hall': 'setonhall',
        'st johns': 'saintjohns',
        'saint louis': 'saintlouis',
        'brigham young': 'byu',
        'colorado state': 'coloradostate',
        'louisiana tech': 'louisianatech',
        'loyola chicago': 'loyolachicago',
        'miami (fl)': 'miami',
        'saint bonaventure': 'saintbonaventure',
        'saint marys': 'saintmarys',
        'utah state': 'utahstate',
        'san francisco': 'sfu',
        'st marys ca': 'saintmarysca',
    }
    name = name.lower()
    for key in dictNames:
        if key in name:
            name = name.replace(key, dictNames[key])
            break
    return name


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
                odds = odds.replace('O', 'o')
                odds = odds.replace('U', 'u')
                odds = odds.replace('\xa0', '')
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
                self.teams_list.append(formatTeamName(teamName))
                self.spreads_list.append(spread)
                self.odds_list.append(odds)
                self.moneylines_list.append(moneyline)

    def displayData(self):
        self.retrieveData()
        self.sortData()
        self.df = pd.DataFrame()
        self.df = pd.concat(
            [self.df, pd.DataFrame({'Team': self.teams_list}), pd.DataFrame({'Spread': self.spreads_list}),
             pd.DataFrame({'Odds': self.odds_list}), pd.DataFrame({'Moneyline': self.moneylines_list})], axis=1)
        self.df = self.df.fillna('')
        return self.df


# %%
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
scraping_list_NFL = [[4, 0, 'nfl', 'football/88670561'],
                     [4, 5, 'nfl1h', 'football/88670561?category=halves&subcategory=1st-half'],
                     [4, 10, 'nfl2h', 'football/88670561?category=halves&subcategory=2nd-half'],
                     [4, 15, 'nfl1q', 'football/88670561?category=quarters&subcategory=1st-quarter'],
                     [4, 20, 'nfl2q', 'football/88670561?category=quarters&subcategory=2nd-quarter'],
                     [4, 25, 'nfl3q', 'football/88670561?category=quarters&subcategory=3rd-quarter'],
                     [4, 30, 'nfl4q', 'football/88670561?category=quarters&subcategory=4th-quarter']]

scraping_list_CFB = [[3, 0, 'ncaaf', 'football/88670775'],
                     [3, 5, 'ncaaf1h', 'football/88670775?category=halves&subcategory=1st-half'],
                     [3, 10, 'ncaaf2h', 'football/88670775?category=halves&subcategory=2nd-half'],
                     [3, 15, 'ncaaf1q', 'football/88670775?category=quarters&subcategory=1st-quarter'],
                     [3, 20, 'ncaaf2q', 'football/88670775?category=quarters&subcategory=2nd-quarter'],
                     [3, 25, 'ncaaf3q', 'football/88670775?category=quarters&subcategory=3rd-quarter'],
                     [3, 30, 'ncaaf4q', 'football/88670775?category=quarters&subcategory=4th-quarter']]

scraping_list_NBA = [[2, 0, 'nba', 'basketball/88670846'],
                     [2, 5, 'nba1h', 'basketball/88670846?category=halves&subcategory=1st-half'],
                     [2, 10, 'nba2h', 'basketball/88670846?category=halves&subcategory=2nd-half'],
                     [2, 15, 'nba1q', 'basketball/88670846?category=quarters&subcategory=1st-quarter'],
                     [2, 20, 'nba2q', 'basketball/88670846?category=quarters&subcategory=2nd-quarter'],
                     [2, 25, 'nba3q', 'basketball/88670846?category=quarters&subcategory=3rd-quarter'],
                     [2, 30, 'nba4q', 'basketball/88670846?category=quarters&subcategory=4th-quarter']]

scraping_list_CBB = [[1, 0, 'ncaab', 'basketball/88670771', 'B:E', 1],
                     [1, 5, 'ncaab1h', 'basketball/88670771?category=halves&subcategory=1st-half'],
                     [1, 10, 'ncaab2h', 'basketball/88670771?category=halves&subcategory=2nd-half'],
                     [1, 15, 'ncaab1q', 'basketball/88670771?category=quarters&subcategory=1st-quarter'],
                     [1, 20, 'ncaab2q', 'basketball/88670771?category=quarters&subcategory=2nd-quarter'],
                     [1, 25, 'ncaab3q', 'basketball/88670771?category=quarters&subcategory=3rd-quarter'],
                     [1, 30, 'ncaab4q', 'basketball/88670771?category=quarters&subcategory=4th-quarter']]

# Determining sports and leageus to scrape
options = input('CBB, NBA, CFB, NFL\nWhat data do you want to scrape? ')
scraping_list = []
body = {"requests": []}

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
        worksheetNumber = sh.get_worksheet(item[0]).id
        # Write Title onto Spreadsheet
        print('Starting', item[2])
        body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                 "range": {"sheetId": worksheetNumber,
                                                           "startColumnIndex": item[1],
                                                           "startRowIndex": 0,
                                                           "endRowIndex": 2,
                                                           "endColumnIndex": item[1] + 1
                                                           },
                                                 "rows": [{"values": [
                                                     {"userEnteredValue": {"stringValue": item[2]}}
                                                 ]}, {"values": [
                                                     {"userEnteredValue": {"stringValue": "DraftKings"}}
                                                 ]}],
                                                 }
                                 })
        # Collect Data for Title
        obj = SportStatic('https://sportsbook.draftkings.com/leagues/' + item[3])
        df = obj.displayData()
        # Insert Data into Spreadsheet
        body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                 "range": {"sheetId": worksheetNumber,
                                                           "startColumnIndex": item[1] + 1,
                                                           "startRowIndex": 0,
                                                           "endColumnIndex": item[1] + 5,
                                                           },
                                                 "rows": [],
                                                 }
                                 })
        values = [df.columns.values.tolist()] + df.values.tolist()
        for row in values:
            rowData = {"values": []}
            for element in row:
                rowData['values'].append({"userEnteredValue": {"stringValue": element}})
            body['requests'][-1]['updateCells']['rows'].append(rowData)
    sh.batch_update(body)
    print('Updated')
