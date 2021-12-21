import time
import requests
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def getRange(index):
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


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
                    if "PROPS" not in subsport.text:
                        try:
                            subsport.find_element(By.CSS_SELECTOR, "a").click()
                        except:
                            pass

    def retrieveData(self):
        html = self.driver.page_source
        # self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        for event in self.soup.find_all(class_='panel panel-transparent'):
            try:
                eventType = event.find(class_='panel-title linesPanelTitle').text
                # creates a new list eventType in the allBets dictionary, which will hold
                # dicts of the micro betting events
                self.allBets[eventType] = []
            # if no attribute of event is found, then
            # set attr to empty string
            except:
                pass

            # create a temporary dictionary to hold the event
            tempEvent = {}
            panelRows = event.find(class_='panel-body').select('div.row')

            # variables to help identify new team matchups
            prevID = -1
            isNew = True
            # TODO fix for futures, not just h2h matchups
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


gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")

website = SportDynamic('https://www.purewage.com/')
sh.get_worksheet(1).clear()
sh.get_worksheet(2).clear()
sh.get_worksheet(3).clear()
sh.get_worksheet(4).clear()

# %%
website.collectData()
# website.launchDriver()
# website.enterDriver()
#
# #%%
# website.retrieveData()
# %%
while True:

    print('Starting')

    startingIndexCBB = 0
    startingIndexNBA = 0
    startingIndexCFB = 0
    startingIndexNFL = 0
    startingIndex = 0
    # TODO purewage missing basketball in allbets dict
    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = formatKey(key)
        bagOfWords = key.split()
        if 'ncaa' in bagOfWords and 'basketball' in bagOfWords:
            print('NCAA Basketball')
            worksheet = sh.get_worksheet(1)
            while len(worksheet.col_values(startingIndexCBB + 1)) > 0:
                startingIndexCBB += 5
            startingIndexCBB += 5
            startingIndex = startingIndexCBB
        elif 'nba' in bagOfWords:
            print('NBA')
            worksheet = sh.get_worksheet(2)
            while len(worksheet.col_values(startingIndexNBA + 1)) > 0:
                startingIndexNBA += 5
            startingIndexNBA += 5
            startingIndex = startingIndexNBA
        elif 'ncaa' in bagOfWords and 'football' in bagOfWords:
            print('NCAA Football')
            worksheet = sh.get_worksheet(3)
            while len(worksheet.col_values(startingIndexCFB + 1)) > 0:
                startingIndexCFB += 5
            startingIndexCFB += 5
            startingIndex = startingIndexCFB
        elif 'nfl' in bagOfWords:
            print('NFL')
            worksheet = sh.get_worksheet(4)
            while len(worksheet.col_values(startingIndexNFL + 1)) > 0:
                startingIndexNFL += 5
            startingIndexNFL += 5
            startingIndex = startingIndexNFL
        else:
            continue
        # TODO implement batch update
        worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Purewage"]])
        worksheet.update(getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                         [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())
        worksheet.format(getRange(startingIndex - 5) + ':' + getRange(startingIndex - 1), {
            "backgroundColor": {
                "red": 0.25,
                "green": 0.5,
                "blue": 0.95
            },
        })

    print('Updated')

    website.driver.find_element(By.XPATH, '//a[text()="Refresh Lines"]').click()

    time.sleep(30)
