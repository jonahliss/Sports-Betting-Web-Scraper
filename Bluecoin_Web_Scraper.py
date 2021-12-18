import codecs
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class SportDynamic:
    def __init__(self, url):
        self.allBets = {}
        self.url = url

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
        # TODO change the selenium to only select relevant sports
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_WagerLnk_lnkSports").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#WT35").click()
        time.sleep(2)
        menus = self.driver.find_elements(By.CSS_SELECTOR, "table[class='sp_hdr'] > tbody > tr > th > table > tbody > "
                                                           "tr > td > a")
        # open up all the menus
        for menu in menus:
            if menu.text != "VIEW ALL":
                menu.click()
        sports = self.driver.find_elements(By.CSS_SELECTOR, "div[class='sw_sp_tbl'] > table > tbody > tr > td")

        time.sleep(.5)
        # click all the checkboxes in the menu that opens up
        for sport in sports:
            buttons = sport.find_elements(By.CSS_SELECTOR, "div > span > input")
            for button in buttons:
                try:
                    button.click()
                except:
                    pass

        self.driver.find_element(By.CSS_SELECTOR, ".contButtTd > a").click()

    def retrieveData(self):
        html = self.driver.page_source
        # self.driver.quit()
        soup = BeautifulSoup(html, "html.parser")
        for event in soup.select('table > tbody')[1:41]:
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

    def presentData(self):
        self.launchDriver()
        self.enterDriver()
        self.navigateDriver()
        self.retrieveData()
        df = pd.DataFrame()
        for event in self.allBets['NFL']:
            for item in event:
                df = pd.concat([df, pd.DataFrame({'Teams': event[item]['team'], 'Spreads': event[item]['spread'],
                                                  'Odds': event[item]['odds'],
                                                  'Moneyline': event[item]['moneyline']})], axis=0)
        df = df.fillna('')
        return df

#%%
# Bluecoin All
NFL = SportDynamic('http://bluecoin.ag/core/mobile/')
print(NFL.presentData())
