import math
import time
import requests
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Function to help organize Google Sheet
def getRange(index):
    if (index - 26) / math.pow(26, 2) >= 1:
        return chr(64 + (index // int(math.pow(26, 2)))) + chr(
            65 + (((index - 26) % int(math.pow(26, 2))) // 26)) + chr(
            65 + (index % 26))
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


# Function to classify HTML class text as a team's name, spread, odds, or moneyline
def determineChild(child):
    global teamName, spread, odds, moneyline
    teamName, spread, odds, moneyline = 'NaN', 'NaN', 'NaN', 'NaN'
    for i in range(4):
        try:
            temp = child.find_all('label')[i].text

            if temp == child.find_all('label')[0].text:
                teamName = temp
                teamName = formatTeamName(teamName)
            elif 'o' in temp or 'u' in temp:
                odds = temp
                odds = odds.replace("½", ".5")
            elif (temp.count('+') + temp.count('-')) == 2:
                spread = temp
            elif (temp.count('+') + temp.count('-')) == 1:
                moneyline = temp
        except:
            pass
    return teamName, spread, odds, moneyline


# Function to standardize text formatting across websites
def formatKey(key):
    key = key.lower()
    key = key.replace("quarters", "1q")
    key = key.replace("quarter", "q")
    key = key.replace("half", "h")
    key = key.replace("1st", "1")
    key = key.replace("2nd", "2")
    key = key.replace("3rd", "3")
    key = key.replace("4th", "4")
    key = key.replace("ncaa basketball", "ncaab")
    key = key.replace("ncaa football", "ncaaf")
    key = key.replace("college football", "ncaaf")
    key = key.replace("margin of victory", "mov")
    key = key.replace("basketball", "b")
    key = key.replace("football", "f")
    key = key.replace("(", "")
    key = key.replace(")", "")
    key = key.replace("-", "")
    key = key.replace(" ", "")
    key = key.replace("lines", "")
    key = key.replace("men", "")
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
        'south carolina': 'southcarolina',
        'iowa state': 'iowastate',
        'oklahoma state': 'oklahomastate',
        'kansas state': 'kansasstate',
        'texas tech': 'texastech',
        'west virginia': 'westvirginia',
        'notre dame': 'notredame',
        'florida state': 'floridastate',
        'georgia tech': 'georgiatech',
        'nc state': 'ncstate',
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
        'miami ohio': 'miamiohio',
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
        'miami florida': 'miami',
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
    name = name.replace("1h ", "")
    name = name.replace("1q ", "")
    return name


# Class to retrieve, sort, and return website data
class SportDynamic:
    def __init__(self, url, options):
        self.url = url
        self.options = options
        self.soup = ""
        self.allBets = {}

    def launchDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)

    def enterDriver(self):
        self.driver.find_element(By.NAME, "Account").send_keys("Efind1")
        self.driver.find_element(By.NAME, "Password").send_keys("123")
        self.driver.find_element(By.XPATH, '//button[text()=" Login"]').click()

    def navigateDriver(self):
        self.driver.find_element(By.ID, "ctl00_lnkSports").click()

        leagues = []
        if 'CBB' in self.options:
            leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_COLLEGEBASKETBALL'))
        if 'NBA' in self.options:
            leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_BASKETBALL'))
        if 'CFB' in self.options:
            leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_COLLEGEFOOTBALL'))
        if 'NFL' in self.options:
            leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_FOOTBALL'))

        for button in leagues:
            button = button.find_element(By.CSS_SELECTOR, '.divLeagueContainer > a')
            if button.text == "Check All":
                button.click()
            if button.text == "Check All":
                button.click()

        self.driver.find_element(By.ID, "continue-2").click()

    def retrieveData(self):
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")
        '''self.driver.quit()'''

    def sortData(self):
        self.allBets = {}
        for event in self.soup.select('div.line'):
            eventType = event.select('h4')[0].text

            tempEvent = {}

            # gets the name of the event as a html tag
            eventName = event.select('div > div > h6')[0]
            tempEvent[eventName.text] = {}

            # gets the team and spreads of the event
            bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
            children = event.find_all('div', class_='row py-4')

            for child in children:
                determineChild(child)
                countNulls = 0
                if teamName != "NaN" and teamName != "":
                    if spread == "NaN":
                        countNulls += 1
                    if odds == "NaN":
                        countNulls += 1
                    if moneyline == "NaN":
                        countNulls += 1
                    if countNulls >= 2 and 'props' not in eventType:
                        eventType += ' props'
                    bettingData["team"].append(teamName)
                    bettingData["spread"].append(spread)
                    bettingData["odds"].append(odds)
                    bettingData["moneyline"].append(moneyline)

            if eventType not in self.allBets:
                self.allBets[eventType] = []
            # sets the betting data of the temporary event
            tempEvent[eventName.text] = bettingData
            # puts the event into the list of all events
            self.allBets[eventType].append(tempEvent)

    def displayData(self, sport):
        df = pd.DataFrame()
        for event in self.allBets[sport]:
            for item in event:
                df = pd.concat([df, pd.DataFrame({'Teams': event[item]['team'], 'Spreads': event[item]['spread'],
                                                  'Odds': event[item]['odds'],
                                                  'Moneyline': event[item]['moneyline']})], axis=0)
        df = df.fillna('')
        return df

    def collectData(self):
        self.launchDriver()
        self.enterDriver()
        self.navigateDriver()
        self.retrieveData()
        self.sortData()


# %%
# Establishing connection with Google Sheets
gc = gspread.service_account(filename='credentials.json')
sh = gc.open("BettingScraper")

# Determining sports and leageus to scrape
options = input('CBB, NBA, CFB, NFL\nWhat data do you want to scrape? ')

# Executing scraping process
website = SportDynamic('https://ubet.ag/', options)
website.collectData()

startTime = time.perf_counter()

while True:

    print('Starting')

    startingIndexCBB = 1800
    startingIndexNBA = 1800
    startingIndexCFB = 1800
    startingIndexNFL = 1800
    startingIndex = 1800
    body = {"requests": []}
    checkProps = {'isProps': False, 'didSetProps': [], 'propsCols': [], 'propsRows': [], 'propsLeagues': []}

    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = key.lower()
        bagOfWords = key.split()
        checkProps['isProps'] = 'props' in bagOfWords or 'futures' in bagOfWords
        if 'ncaa' in bagOfWords and ('basketball' in bagOfWords or '(b)' in bagOfWords):
            print('NCAA Basketball')
            try:
                worksheet = sh.get_worksheet(1)
            except:
                failTime = time.perf_counter()
                pause = 101 - (failTime - startTime)
                print('Pausing for', pause, 'seconds')
                time.sleep(pause)
                print('Resuming')
                gc = gspread.service_account(filename='credentials.json')
                sh = gc.open("BettingScraper")
                worksheet = sh.get_worksheet(1)
                startTime = time.perf_counter()
            startingIndexCBB += 5
            startingIndex = startingIndexCBB
            time.sleep(0.6)
        elif 'nba' in bagOfWords:
            print('NBA')
            try:
                worksheet = sh.get_worksheet(2)
            except:
                failTime = time.perf_counter()
                pause = 101 - (failTime - startTime)
                print('Pausing for', pause, 'seconds')
                time.sleep(pause)
                print('Resuming')
                gc = gspread.service_account(filename='credentials.json')
                sh = gc.open("BettingScraper")
                worksheet = sh.get_worksheet(2)
                startTime = time.perf_counter()
            startingIndexNBA += 5
            startingIndex = startingIndexNBA
            time.sleep(0.6)
        elif 'ncaa' in bagOfWords and ('football' in bagOfWords or '(f)' in bagOfWords):
            print('NCAA Football')
            try:
                worksheet = sh.get_worksheet(3)
            except:
                failTime = time.perf_counter()
                pause = 101 - (failTime - startTime)
                print('Pausing for', pause, 'seconds')
                time.sleep(pause)
                print('Resuming')
                gc = gspread.service_account(filename='credentials.json')
                sh = gc.open("BettingScraper")
                worksheet = sh.get_worksheet(3)
                startTime = time.perf_counter()
            startingIndexCFB += 5
            startingIndex = startingIndexCFB
            time.sleep(0.6)
        elif 'nfl' in bagOfWords:
            print('NFL')
            try:
                worksheet = sh.get_worksheet(4)
            except:
                failTime = time.perf_counter()
                pause = 101 - (failTime - startTime)
                print('Pausing for', pause, 'seconds')
                time.sleep(pause)
                print('Resuming')
                gc = gspread.service_account(filename='credentials.json')
                sh = gc.open("BettingScraper")
                worksheet = sh.get_worksheet(4)
                startTime = time.perf_counter()
            startingIndexNFL += 5
            startingIndex = startingIndexNFL
            time.sleep(0.6)
        else:
            continue
        key = formatKey(key)
        # checks if the props for each league is new, and if so, resets the starting column and row
        if worksheet.id not in checkProps['propsLeagues']:
            checkProps['propsLeagues'].append(worksheet.id)
            checkProps['propsCols'].append(-1)
            checkProps['propsRows'].append(0)
            checkProps['didSetProps'].append(False)
        leagueIndex = checkProps['propsLeagues'].index(worksheet.id)
        # find the unique spreadsheet id
        worksheetNumber = worksheet.id
        values = [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist()
        # create body for the google sheets batch update api
        if checkProps['isProps']:
            # set the props column index to the first time a props event appears
            if not checkProps['didSetProps'][leagueIndex]:
                checkProps['didSetProps'][leagueIndex] = True
                checkProps['propsCols'][leagueIndex] = startingIndex - 5
            # update the body dictionary to a single column
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": checkProps['propsCols'][leagueIndex],
                                                               "startRowIndex": checkProps['propsRows'][leagueIndex],
                                                               "endRowIndex": checkProps['propsRows'][leagueIndex] + 2,
                                                               "endColumnIndex": checkProps['propsCols'][
                                                                                     leagueIndex] + 1,
                                                               },
                                                     "rows": [{"values": [
                                                         {"userEnteredValue": {"stringValue": key}}
                                                     ]}, {"values": [
                                                         {"userEnteredValue": {"stringValue": "Ubet props"}}
                                                     ]}
                                                     ], }
                                     })
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": checkProps['propsCols'][
                                                                                       leagueIndex] + 1,
                                                               "startRowIndex": checkProps['propsRows'][leagueIndex],
                                                               "endColumnIndex": checkProps['propsCols'][
                                                                                     leagueIndex] + 5,
                                                               },
                                                     "rows": [],
                                                     }
                                     })
            checkProps['propsRows'][leagueIndex] += len(values)
        else:
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": startingIndex - 5,
                                                               "startRowIndex": 0,
                                                               "endRowIndex": 2,
                                                               "endColumnIndex": startingIndex - 4,
                                                               },
                                                     "rows": [{"values": [
                                                         {"userEnteredValue": {"stringValue": key}}
                                                     ]}, {"values": [
                                                         {"userEnteredValue": {"stringValue": "Ubet"}}
                                                     ]}],
                                                     }
                                     })
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": startingIndex - 4,
                                                               "startRowIndex": 0,
                                                               "endColumnIndex": startingIndex,
                                                               },
                                                     "rows": [],
                                                     }
                                     })
        for row in values:
            rowData = {"values": []}
            for element in row:
                rowData['values'].append({"userEnteredValue": {"stringValue": element}})
            body['requests'][-1]['updateCells']['rows'].append(rowData)
    sh.batch_update(body)
    print('Updated')

    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
    website.retrieveData()
    website.sortData()
