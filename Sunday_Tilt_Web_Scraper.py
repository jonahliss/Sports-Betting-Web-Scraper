import math
import time
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
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


# Function to standardize text formatting across websites
def formatKey(key):
    key = key.lower()
    key = key.replace("quarter", "q")
    key = key.replace("half", "h")
    key = key.replace("1st", "1")
    key = key.replace("2nd", "2")
    key = key.replace("3rd", "3")
    key = key.replace("4th", "4")
    key = key.replace("½", ".5")
    key = key.replace("ncaa basketball", "ncaab")
    key = key.replace("ncaa football", "ncaaf")
    key = key.replace("college football", "ncaaf")
    key = key.replace("margin of victory", "mov")
    key = key.replace("scoring play", "sp")
    key = key.replace("alternate lines", "al")
    key = key.replace("game props", "gp")
    key = key.replace("player props", "pp")
    key = key.replace("live betting", "lb")
    key = key.replace("2020/21", "")
    key = key.replace("2021/22", "")
    key = key.replace("(", "")
    key = key.replace(")", "")
    key = key.replace("-", "")
    key = key.replace(" ", "")
    key = key.replace("basketball", "")
    key = key.replace("football", "")
    key = key.replace("men", "")
    key = key.replace("odds to win", "")
    key = key.replace("lines", "")
    key = key.replace("nan", "NaN")
    return key


def formatTeamName(name):
    dictNames = {
        'ohio st': 'ohiostate',
        'michigan st': 'michiganstate',
        'penn st': 'pennstate',
        'texas a&m': 'texasanm',
        'w michigan': 'westernmichigan',
        'air force': 'airforce',
        'mississippi st': 'mississippistate',
        'south carolina': 'southcarolina',
        's carolina': 'southcarolina',
        'iowa st': 'iowastate',
        'oklahoma st': 'oklahomastate',
        'kansas st': 'kansasstate',
        'texas tech': 'texastech',
        'w virginia': 'westvirginia',
        'west virginia': 'westvirginia',
        'notre dame': 'notredame',
        'florida st': 'floridastate',
        'georgia tech': 'georgiatech',
        'north carolina': 'northcarolina',
        'nc state': 'ncstate',
        'va tech': 'virginiatech',
        'virginia tech': 'virginiatech',
        'boston college': 'bostoncollege',
        'wake forest': 'wakeforest',
        'washington st': 'washingtonstate',
        'oregon st': 'oregonstate',
        'arizona st': 'arizonastate',
        'central michigan': 'centralmichigan',
        'eastern michigan': 'easternmichigan',
        'central florida': 'centralflorida',
        'miami ohio': 'miamiohio',
        'western kentucky': 'westernkentucky',
        'boise st': 'boisestate',
        'fresno st': 'fresnostate',
        'wichita st': 'wichita',
        'seton hall': 'setonhall',
        'st johns': 'saintjohns',
        'saint louis': 'saintlouis',
        'brigham young': 'byu',
        'colorado st': 'coloradostate',
        'louisiana tech': 'louisianatech',
        'loyola chicago': 'loyolachicago',
        'miami florida': 'miami',
        'saint bonaventure': 'saintbonaventure',
        'saint marys': 'saintmarys',
        'utah st': 'utahstate',
        'san francisco': 'sfu',
        'st marys ca': 'saintmarysca',
    }
    name = name.lower()
    for key in dictNames:
        if key in name:
            name = name.replace(key, dictNames[key])
            break
    return name


# Class to retrieve, sort, and return website data
class SportDynamic:
    def __init__(self, url):
        self.url = url
        self.soup = ""
        self.allBets = {}
        self.sport = ""

    def launchDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
        time.sleep(1)

    def enterDriver(self):
        username = self.driver.find_element(By.NAME, "customerID")
        password = self.driver.find_element(By.NAME, "Password")
        username.send_keys("Gh75")
        password.send_keys("soccer1")
        self.driver.find_element(By.XPATH, '//button[text()="LOGIN"]').click()

    def navigateDriver(self):
        time.sleep(12)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "div[data-allow='BASKETBALL'] a").click()
            self.driver.find_element(By.CSS_SELECTOR, "div[data-allow='HALFTIMES'] a").click()
            self.driver.find_element(By.CSS_SELECTOR, "div[data-allow='LIVE'] a").click()
        except:
            pass
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(1)
        # inserts the sport and league into the appropriate css locator
        enter_live = self.driver.find_elements(By.CSS_SELECTOR,
                                               "#{} > div > ul > li".format("LIVE"))
        enter_nfl = self.driver.find_elements(By.CSS_SELECTOR,
                                              "#{} > div > ul > li".format("FOOTBALL"))
        enter_nfl[0].find_element(By.CSS_SELECTOR, 'div').click()
        enter_nba = self.driver.find_elements(By.CSS_SELECTOR,
                                              "#{} > div > ul > li".format("BASKETBALL"))

        for checkbox in enter_live:
            try:
                checkbox.find_element(By.CSS_SELECTOR, 'div').click()
            except:
                pass
        for checkbox in enter_nfl:
            try:
                if checkbox.get_attribute("data-sub-event") != None:
                    checkbox.find_element(By.CSS_SELECTOR, '.accordion-heading').click()
                    time.sleep(.5)
                    nested_checkbox = checkbox.find_elements(By.CSS_SELECTOR,
                                                             "div[data-field='link-parent'] > div > ul > li")
                    for nested in nested_checkbox:
                        nested.find_element(By.CSS_SELECTOR, 'div').click()
                else:
                    checkbox.find_element(By.CSS_SELECTOR, 'div').click()
            except:
                pass
        for checkbox in enter_nba:
            try:
                if checkbox.get_attribute("data-sub-event") != None:
                    checkbox.find_element(By.CSS_SELECTOR, '.accordion-heading').click()
                    time.sleep(.5)
                    nested_checkbox = checkbox.find_elements(By.CSS_SELECTOR,
                                                             "div[data-field='link-parent'] > div > ul > li")
                    for nested in nested_checkbox:
                        nested.find_element(By.CSS_SELECTOR, 'div').click()
                else:
                    checkbox.find_element(By.CSS_SELECTOR, 'div').click()
            except:
                pass

    def retrieveData(self):
        time.sleep(4)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        self.allBets = {}
        for event in self.soup.select('div.page-lines > div')[:-2]:
            # tries to find the "header-a" tags that hold the event types
            try:
                eventType = event.find(class_='header-a').div.span.text
                eventType = eventType + " " + \
                            event.find(class_='header-a').find(class_='league-icon').i['class'][0].split('-')[1]
                # creates a new list eventType in the allBets dictionary, which will hold
            except:
                pass
            # create a temporary dictionary to hold the event
            tempEvent = {}
            try:
                eventName = event.find(class_='header-d').select('div > span')[2].text
            except:
                eventName = 'null event name'
            # gets the team and spreads of the event
            bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}

            # gets the name of the event as a html tag
            teams = event.select('div.lines > div')
            if len(teams) == 0:
                continue

            if len(teams) == 3:
                futures = teams[0].select('div.group')
                try:
                    teamName = futures[0].find('div', class_='team').select('span')[1].text
                    teamName = formatTeamName(teamName)
                except:
                    teamName = "NaN"
                try:
                    moneyline = futures[1].find('div', class_='line-play').span.text
                except:
                    moneyline = "NaN"
                odds = "NaN"
                spread = "NaN"
                bettingData["team"].append(teamName)
                bettingData["spread"].append(spread)
                bettingData["odds"].append(odds)
                bettingData["moneyline"].append(moneyline)
                if 'props' not in eventType:
                    eventType += ' props'

            else:
                for team in teams:
                    data = team.find_all('div', recursive=False)
                    try:
                        teamName = data[0].select('div.team > span')[0].text
                        teamName = formatTeamName(teamName)
                    except:
                        teamName = "NaN"
                    try:
                        spread = data[1].select('div > span')[0].text
                    except:
                        spread = "NaN"
                    try:
                        odds = data[3].select('div > span')[0].text
                        odds = odds.replace('O ', 'o')
                        odds = odds.replace('U ', 'u')
                        odds = odds.replace("½", ".5")
                    except:
                        odds = "NaN"
                    try:
                        moneyline = data[2].select('div > span')[0].text
                    except:
                        moneyline = "NaN"

                    bettingData["team"].append(teamName)
                    bettingData["spread"].append(spread)
                    bettingData["odds"].append(odds)
                    bettingData["moneyline"].append(moneyline)

            # create unique key for the event
            eventName = eventName + ": " + teamName

            # sets the betting data of the temporary event
            tempEvent[eventName] = bettingData
            # dicts of the micro betting events
            if eventType not in self.allBets:
                self.allBets[eventType] = []
            # append onto the list of events, the dict of the micro betting events
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

# Executing scraping process
website = SportDynamic('https://www.sundaytilt.com/')
website.collectData()

#%%

listNFLteams = ['afc', 'nfc', 'nfl', 'division', 'super', 'mvp', 'cardinals', 'falcons', 'ravens', 'bills', 'panthers',
                'bears', 'bengals', 'browns', 'cowboys', 'broncos',
                'lions', 'packers', 'texans', 'colts', 'jaguars',
                'chiefs', 'chargers', 'rams', 'dolphins', 'vikings',
                'patriots', 'saints', 'giants', 'jets', 'raiders',
                'eagles', 'steelers', '49ers', 'seahawks',
                'buccaneers', 'titans', 'team']

listNBAteams = ['nba', 'eastern conference', 'western conference', 'celtics', 'nets', 'hornets', 'bulls', 'cavaliers',
                'mavericks', 'heat', 'bucks', 'pacers', 'knicks', 'sixers', 'clippers', 'lakers', 'grizzlies',
                'warriors', 'rockets', 'pacers', 'thunder', 'timberwolves', 'pelicans', 'magic', '76ers', 'suns',
                'blazers', 'kings', 'spurs', 'raptors', 'jazz', 'wizards', 'pistons']

listCollegeTeams = ['ohio st', 'michigan', 'michigan st', 'penn st', 'wisconsin', 'northwestern', 'illinois', 'rutgers',
                    'maryland', 'indiana', 'iowa', 'nebraska', 'minnesota', 'purdue', 'alabama', 'lsu', 'texas a&m',
                    'mississippi st', 'ole miss', 'mississippi', 'arkansas', 'georgia', 'kentucky', 'vanderbilt',
                    'tennessee', 'florida', 'missouri', 'south carolina', 's carolina', 'auburn', 'iowa st',
                    'oklahoma st', 'texas', 'oklahoma', 'baylor', 'tcu', 'kansas st', 'kansas', 'texas tech',
                    'w virginia', 'west virginia', 'notre dame', 'clemson', 'miami', 'florida st', 'georgia tech',
                    'north carolina', 'n carolina', 'unc', 'nc state', 'va tech', 'virginia', 'pittsburgh',
                    'boston college', 'boston coll', 'syracuse', 'wake forest', 'duke', 'louisville', 'washington',
                    'washington st', 'oregon', 'oregon st', 'ucla', 'cal', 'usc', 'stanford', 'asu', 'arizona st',
                    'arizona', 'utah', 'colorado', 'cincinnati', 'w michigan', 'c michigan', 'e michigan', 'memphis',
                    'houston', 'ucf', 'c florida', 'miami ohio', 'miami oh', 'w kentucky', 'nevada', 'boise st',
                    'wyoming', 'fresno st', 'sdsu', 'wichita st', 'gonzaga', 'villanova', 'georgetown', 'seton hall',
                    'creighton', 'butler', 'depaul', 'st johns', 'uconn', 'connecticut', 'liberty', 'dayton',
                    'marquette', 'saint louis', 'providence', 'belmont', 'buffalo', 'byu', 'brigham young',
                    'colorado st', 'louisiana tech', 'smu', 'drake', 'loyola chicago', 'miami florida', 'richmond',
                    'saint johns', 'saint bonaventure', 'saint marys', 'pepperdine', 'uab', 'usf', 'utah st', 'vcu',
                    'xavier', 'marquette', 'san francisco', 'hawaii', 'unlv', 'ncaa', 'college', 'ncaaf', 'ncaab']

startTime = time.perf_counter()

while True:

    print('Starting')

    startingIndexCBB = 1200
    startingIndexNBA = 1200
    startingIndexCFB = 1200
    startingIndexNFL = 1200
    startingIndex = 1200
    body = {"requests": []}
    checkProps = {'isProps': False, 'didSetProps': [], 'propsCols': [], 'propsRows': [], 'propsLeagues': []}

    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = key.lower()
        bagOfWords = key.split()
        isCollege = False
        isNFL = False
        isNBA = False
        checkProps['isProps'] = 'props' in bagOfWords or 'futures' in bagOfWords
        # checks if the event name is a college event
        for temp in bagOfWords:
            if temp in listNFLteams:
                isNFL = True
                break
            elif temp in listNBAteams:
                isNBA = True
                break
            elif temp in listCollegeTeams:
                isCollege = True
                break
        if isNBA:
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
        elif isNFL:
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
        elif 'basketball' in bagOfWords or (isCollege and 'ncaab' in bagOfWords):
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
        elif 'football' in bagOfWords or (isCollege and 'ncaaf' in bagOfWords):
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
                                                               "endColumnIndex": checkProps['propsCols'][leagueIndex] + 1,
                                                               },
                                                     "rows": [{"values": [
                                                         {"userEnteredValue": {"stringValue": key}}
                                                     ]}, {"values": [
                                                         {"userEnteredValue": {"stringValue": "Sundaytilt props"}}
                                                     ]}
                                                     ], }
                                     })
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": checkProps['propsCols'][leagueIndex] + 1,
                                                               "startRowIndex": checkProps['propsRows'][leagueIndex],
                                                               "endColumnIndex": checkProps['propsCols'][leagueIndex] + 5,
                                                               },
                                                     "rows": [],
                                                     }
                                     })
            checkProps['propsRows'][leagueIndex] += len(values)
        # create body for the google sheets batch update api
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
                                                         {"userEnteredValue": {"stringValue": "Sundaytilt"}}
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

    website.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(1)
    website.driver.find_element(By.CSS_SELECTOR, "div[data-wager-type='REFRESH']").click()
    website.retrieveData()
    website.sortData()
