import math
import time
import requests
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
        self.allBets = {}
        self.url = url
        self.options = options
        self.soup = ""

    def launchDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)

    def enterDriver(self):
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_MainContent_LoginControl1__UserName").send_keys("Lin257")
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_MainContent_LoginControl1__Password").send_keys("2873")
        time.sleep(.5)
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_MainContent_LoginControl1_BtnSubmit").click()

    def navigateDriver(self):
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_WagerLnk_lnkSports").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#WT35").click()
        time.sleep(2)
        menus = self.driver.find_elements(By.CSS_SELECTOR, "a[class='league_switch']")[:5]
        # open up all the menus
        for menu in menus:
            if menu.text in self.options:
                menu.click()
                time.sleep(.5)

        time.sleep(1)
        sports = self.driver.find_elements(By.CSS_SELECTOR, "table[class='sp_tbl']")
        # click all the checkboxes in the menu that opens up
        for sport in sports:
            buttons = sport.find_elements(By.CSS_SELECTOR, "tbody > tr > td > div > span > input")
            for button in buttons:
                try:
                    button.click()
                    time.sleep(.05)
                except:
                    pass

        self.driver.find_element(By.CSS_SELECTOR, ".contButtTd > a").click()

    def retrieveData(self):
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")
        '''self.driver.quit()'''

    def sortData(self):
        self.allBets = {}
        for event in self.soup.select('table > tbody')[1:41]:

            # create a temporary dictionary to hold the event
            tempEvent = {}

            # select all the table rows we want by class
            tableRows = event.select('tr.TrGameOdd')
            for temp in event.select('tr.TrGameEven'):
                tableRows.append(temp)
            # include the futures rows?
            tableFutureRows = event.select('tr.TrTntDetail')
            # try to find the event type in the first td element of the table
            try:
                eventType = event.find('td').text
                unknownEventTypeList = []
            except:
                pass

            # variables to help identify new team matchups
            prevID = -1
            isNew = True

            teamName = "NaN"
            spread = "NaN"
            odds = "NaN"
            moneyline = "NaN"

            # iterate through all the game lines and props events
            if len(tableRows) > 1:
                for row in tableRows:
                    cols = row.select('td')
                    # gets the eventID
                    try:
                        eventID = cols[2].text
                        teamName = cols[3].text
                        teamName = formatTeamName(teamName)
                    except:
                        # if eventID not found, it is not a valid event
                        continue

                    for i in range(4, 7):
                        try:
                            temp = cols[i].text
                            if 'o' in temp or 'u' in temp:
                                odds = temp
                                odds = odds.replace("??", ".5")
                            elif (temp.count('+') + temp.count('-')) == 2:
                                spread = temp
                            elif (temp.count('+') + temp.count('-')) == 1:
                                moneyline = temp
                        except:
                            pass

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
                        countNan = 0
                        for dataPoint in bettingData:
                            if "NaN" in bettingData[dataPoint]:
                                countNan += 1
                        if countNan >= 2:
                            eventType += ' props'
                    # append onto the list of events, the dict of the micro betting events
                unknownEventTypeList.append(tempEvent)

            else:  # iterate through the futures
                eventType += ' futures'
                for row in tableFutureRows:
                    cols = row.select('td')
                    bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                    eventName = cols[4].text
                    teamName = cols[4].text
                    teamName = formatTeamName(teamName)

                    for i in range(5, 8):
                        try:
                            temp = cols[i].text

                            if 'o' in temp or 'u' in temp:
                                odds = temp
                            elif (temp.count('+') + temp.count('-')) == 2:
                                spread = temp
                            elif (temp.count('+') + temp.count('-')) == 1:
                                moneyline = temp
                        except:
                            pass

                    bettingData["team"].append(teamName)
                    bettingData["spread"].append(spread)
                    bettingData["odds"].append(odds)
                    bettingData["moneyline"].append(moneyline)
                    tempEvent[eventName] = bettingData
                    # append onto the list of events, the dict of the micro betting events
                unknownEventTypeList.append(tempEvent)
            self.allBets[eventType] = unknownEventTypeList

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
options = input('CFB, NFL, CBB, NBA\nWhat data do you want to scrape? ')

if 'CFB' in options:
    options += 'COLLEGE FOOTBALL, NCAA FB, NCAA FOOTBALL'

if 'CBB' in options:
    options += 'COLLEGE BASKETBALL, NCAA BK, NCAA BASKETBALL'

# Executing scraping process
website = SportDynamic('http://bluecoin.ag/core/mobile/', options)
website.collectData()

startTime = time.perf_counter()

while True:

    print('Starting')

    startingIndexCBB = 2405
    startingIndexNBA = 2405
    startingIndexCFB = 2405
    startingIndexNFL = 2405
    startingIndex = 2405
    body = {"requests": []}
    checkProps = {'isProps': False, 'didSetProps': [], 'propsRows': [], 'propsLeagues': []}

    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = key.lower()
        bagOfWords = key.split()
        checkProps['isProps'] = 'props' in bagOfWords or 'futures' in bagOfWords
        if 'ncaa' and 'bk' in bagOfWords or 'ncaa' and 'basketball' in bagOfWords or 'college' and 'basketball' in bagOfWords:
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
            worksheetNumber = 1
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
            worksheetNumber = 2
            startingIndexNBA += 5
            startingIndex = startingIndexNBA
            time.sleep(0.6)
        elif 'ncaa' and 'fb' in bagOfWords or 'ncaa' and 'football' in bagOfWords or 'college' and 'football' in bagOfWords:
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
            worksheetNumber = 3
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
            worksheetNumber = 4
            startingIndexNFL += 5
            startingIndex = startingIndexNFL
            time.sleep(0.6)
        else:
            continue

        key = formatKey(key)
        # checks if the props for each league is new, and if so, resets the starting column and row
        if worksheet.id not in checkProps['propsLeagues']:
            checkProps['propsLeagues'].append(worksheet.id)
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
            # update the body dictionary to a single column
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": 2400,
                                                               "startRowIndex": checkProps['propsRows'][leagueIndex],
                                                               "endRowIndex": checkProps['propsRows'][leagueIndex] + 2,
                                                               "endColumnIndex": 2401,
                                                               },
                                                     "rows": [{"values": [
                                                         {"userEnteredValue": {"stringValue": key}}
                                                     ]}, {"values": [
                                                         {"userEnteredValue": {"stringValue": "Bluecoin props"}}
                                                     ]}
                                                     ], }
                                     })
            body['requests'].append({"updateCells": {"fields": "userEnteredValue",
                                                     "range": {"sheetId": worksheetNumber,
                                                               "startColumnIndex": 2401,
                                                               "startRowIndex": checkProps['propsRows'][leagueIndex],
                                                               "endColumnIndex": 2405,
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
                                                         {"userEnteredValue": {"stringValue": "Bluecoin"}}
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
    time.sleep(.5)
    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
    website.retrieveData()
    website.sortData()
