import time
import gspread
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def getRange(index):
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)


class SportDynamic:
    def __init__(self, url):
        self.allBets = {}
        self.url = url
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
            if menu.text != "VIEW ALL":
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
        # self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        for event in self.soup.select('table > tbody')[1:41]:
            # try to find the event type in the first td element of the table
            try:
                eventType = event.find('td').text
                self.allBets[eventType] = []
            except:
                pass

            # create a temporary dictionary to hold the event
            tempEvent = {}

            # select all the table rows we want by class
            tableRows = event.select('tr.TrGameOdd')
            for temp in event.select('tr.TrGameEven'):
                tableRows.append(temp)
            # include the futures rows?
            tableFutureRows = event.select('tr.TrTntDetail')

            # variables to help identify new team matchups
            prevID = -1
            isNew = True
            if len(tableRows) > 1:
                for row in tableRows:
                    cols = row.select('td')
                    # gets the eventID
                    try:
                        eventID = cols[2].text
                    except:
                        # if eventID not found, it is not a valid event
                        continue
                    try:
                        teamName = cols[3].text
                    except:
                        teamName = "NaN"
                    try:
                        spread = cols[4].text
                    except:
                        spread = "NaN"
                    try:
                        odds = cols[5].text
                    except:
                        odds = "NaN"
                    try:
                        moneyline = cols[6].text
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

            else:  # iterate through the futures
                for row in tableFutureRows:
                    cols = row.select('td')
                    bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                    eventName = cols[4].text
                    try:
                        teamName = cols[4].text
                    except:
                        teamName = "NaN"
                    try:
                        spread = cols[6].text
                    except:
                        spread = "NaN"
                    try:
                        odds = cols[7].text
                    except:
                        odds = "NaN"
                    try:
                        moneyline = cols[5].text
                    except:
                        moneyline = "NaN"

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

# %%
gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")
worksheet = sh.get_worksheet(5)
worksheet.clear()

website = SportDynamic('http://bluecoin.ag/core/mobile/')
website.collectData()

while True:

    print('Starting')

    startingIndex = 0
    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        worksheet.update(getRange(startingIndex) + str(1), key)
        worksheet.update(getRange(startingIndex + 1) + ':' + getRange(startingIndex + 4),
                         [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())
        startingIndex += 5

    print('Updated')

    time.sleep(30)

    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
