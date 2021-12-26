import math
import time
import requests
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def getRange(index):
    if (index - 26) / math.pow(26, 2) >= 1:
        return chr(64 + (index // int(math.pow(26, 2)))) + chr(
            65 + (((index - 26) % int(math.pow(26, 2))) // 26)) + chr(
            65 + (index % 26))
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


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


class SportDynamic:
    def __init__(self, url):
        self.url = url
        self.allBets = {}
        self.soup = ""

    def launchDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)

    def enterDriver(self):
        self.driver.find_element(By.CSS_SELECTOR, "input[name='account']").send_keys("Efind")
        self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("blue67")
        self.driver.find_element(By.CSS_SELECTOR, ".btn_holder").click()

    def navigateDriver(self):
        time.sleep(1)
        # list of all elements of sport categories
        sports = self.driver.find_elements(By.CSS_SELECTOR, "#sportSide > li")
        for sport in sports:
            if sport.text != "SPORTS" and ("basketball" in sport.text.lower() or "football" in sport.text.lower()):
                sport.find_element(By.CSS_SELECTOR, "a").click()
                time.sleep(.5)
                subsports = sport.find_elements(By.CSS_SELECTOR, "ul > li")
                for subsport in subsports:
                    if "PROPS" not in subsport.text and ("NBA" in subsport.text or "NFL" in subsport.text or "NCAA" in subsport.text):
                        try:
                            subsport.find_element(By.CSS_SELECTOR, "a").click()
                        except:
                            pass

    def retrieveData(self):
        html = self.driver.page_source
        # self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        self.allBets = {}
        for event in self.soup.find_all(class_='panel panel-transparent'):

            # create a temporary dictionary to hold the event
            tempEvent = {}
            panelRows = event.find(class_='panel-body').select('div.row')

            # variables to help identify new team matchups
            prevID = -1
            isNew = True
            # checks first header row to see if it is a prop, future, or h2h matchup
            # 0 is prop, 1 is future, 2 is h2h
            gameType = -1
            numHeaders = len(panelRows[0].select('div'))
            if numHeaders >= 6:
                gameType = 2
            elif numHeaders == 5:
                gameType = 1
            else:
                gameType = 0

            try:
                if gameType == 2:
                    eventType = event.find(class_='panel-title linesPanelTitle').text
                    # creates a new list eventType in the allBets dictionary, which will hold
                    # dicts of the micro betting events
                elif gameType == 1:
                    eventType = event.find('h6').text
                elif gameType == 0:
                    eventType = event.find_all(class_='row gameDate')[1].text
                self.allBets[eventType] = []
            # if no attribute of event is found, then
            # set attr to empty string
            except:
                pass

            # finds the betting data for the h2h matchups
            if gameType == 2:
                for row in panelRows:
                    # gets the eventID
                    try:
                        eventID = row.find(class_='linesRot').text
                    except:
                        # if eventID not found, it is not a valid event
                        continue
                    try:
                        teamName = row.find(class_='linesTeam').select('span')[1].next
                        teamName = str(teamName)
                        teamName = teamName.strip()
                        teamName = teamName.lower()
                    except:
                        teamName = "NaN"
                    try:
                        spread = row.find(class_='linesSpread').find('a').text
                    except:
                        spread = "NaN"
                    try:
                        odds = row.find(class_='linesMl').find('a').text
                        odds = odds.replace('Ov ', 'o')
                        odds = odds.replace('Un ', 'u')
                        odds = odds.replace("½", ".5")
                    except:
                        odds = "NaN"
                    try:
                        moneyline = row.find(class_='linesTotal').find('a').text
                    except:
                        moneyline = "NaN"

                    # if the eventID is "new", create new eventName, and reset the bettingData
                    if int(eventID) - 1 != prevID and isNew:
                        bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                        eventName = str(eventID) + ": " + teamName
                        isNew = False
                        prevID = eventID
                        bettingData["team"].append(teamName)
                        bettingData["spread"].append(spread)
                        bettingData["odds"].append(odds)
                        bettingData["moneyline"].append(moneyline)
                    # eventID has already been reached, so append the data onto list of all events
                    else:
                        isNew = True
                        bettingData["team"].append(teamName)
                        bettingData["spread"].append(spread)
                        bettingData["odds"].append(odds)
                        bettingData["moneyline"].append(moneyline)
                        tempEvent[eventName] = bettingData
            # finds betting data for futures
            elif gameType == 1:
                futuresD = event.find(class_='panel-body').find_all(class_='betting-lines-container tnt row')
                for row in event.find(class_='panel-body').find_all(class_='betting-lines-container tnt row'):
                    # gets the eventID
                    try:
                        teamName = row.div.div.select('div.betting-lines-line-name-prop')[0].span.text
                        teamName = str(teamName)
                        teamName = teamName.replace(eventType, '')
                        teamName = teamName.strip()
                        teamName = teamName.lower()
                        eventName = teamName
                    except:
                        teamName = "NaN"
                        eventName = "NaN"
                    try:
                        moneyline = row.div.div.select('div.betting-lines-line-line-ml')[0].a.text
                    except:
                        moneyline = "NaN"
                    spread = "NaN"
                    odds = "NaN"
                    bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                    bettingData["team"].append(teamName)
                    bettingData["spread"].append(spread)
                    bettingData["odds"].append(odds)
                    bettingData["moneyline"].append(moneyline)
                    tempEvent[eventName] = bettingData
            # finds betting data for props
            elif gameType == 0:
                propsD = panelRows
                for row in panelRows:
                    # gets the eventID
                    try:
                        teamName = row.find(class_='linesTeam').text
                        teamName = str(teamName)
                        teamName = teamName.strip()
                        teamName = teamName.lower()
                        eventName = teamName
                    except:
                        teamName = "NaN"
                        eventName = "NaN"
                    try:
                        moneyline = row.find(class_='linesSpread').find('a').text
                    except:
                        moneyline = "NaN"
                    spread = "NaN"
                    odds = "NaN"
                    bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                    bettingData["team"].append(teamName)
                    bettingData["spread"].append(spread)
                    bettingData["odds"].append(odds)
                    bettingData["moneyline"].append(moneyline)
                    tempEvent[eventName] = bettingData
            else:
                print("Error: gameType not recognized")
                # return

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
gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")

website = SportDynamic('https://www.purewage.com/')
website.collectData()
# website.launchDriver()
# website.enterDriver()
#
# %%
listNFLteams = ['afc', 'nfc', 'nfl', 'division', 'super', 'cardinals', 'falcons', 'ravens', 'bills', 'panthers',
                'bears', 'bengals', 'browns', 'cowboys', 'broncos', 'washington', 'lions', 'packers', 'texans', 'colts',
                'chiefs', 'chargers', 'rams', 'dolphins', 'vikings', 'patriots', 'saints', 'giants', 'jets', 'raiders',
                'eagles', 'steelers', '49ers', 'seahawks', 'buccaneers', 'titans', 'jaguars']

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

while True:

    print('Starting')

    startingIndexCBB = 600
    startingIndexNBA = 600
    startingIndexCFB = 600
    startingIndexNFL = 600
    startingIndex = 600
    body = {"requests": []}
    # TODO purewage missing basketball in allbets dict
    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = key.lower()
        bagOfWords = key.split()
        isCollege = False
        isNFL = False
        isNBA = False
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
            worksheet = sh.get_worksheet(2)
            startingIndexNBA += 5
            startingIndex = startingIndexNBA
        elif isNFL:
            print('NFL')
            worksheet = sh.get_worksheet(4)
            startingIndexNFL += 5
            startingIndex = startingIndexNFL
        # TODO fix college identifation
        elif 'basketball' in bagOfWords or (isCollege and 'ncaab' in bagOfWords):
            print('NCAA Basketball')
            worksheet = sh.get_worksheet(1)
            startingIndexCBB += 5
            startingIndex = startingIndexCBB
        elif 'football' in bagOfWords or (isCollege and 'ncaaf' in bagOfWords):
            print('NCAA Football')
            worksheet = sh.get_worksheet(3)
            startingIndexCFB += 5
            startingIndex = startingIndexCFB
        else:
            continue
        key = formatKey(key)
        # find the unique spreadsheet id
        worksheetNumber = worksheet.id
        # create body for the google sheets batch update api
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
                                                     {"userEnteredValue": {"stringValue": "Purewage"}}
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
        values = [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist()
        for row in values:
            rowData = {"values": []}
            for element in row:
                rowData['values'].append({"userEnteredValue": {"stringValue": element}})
            body['requests'][-1]['updateCells']['rows'].append(rowData)
    sh.batch_update(body)
    print('Updated')

    website.driver.find_element(By.XPATH, '//a[text()="Refresh Lines"]').click()

    time.sleep(30)
