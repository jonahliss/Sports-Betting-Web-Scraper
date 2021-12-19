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
                time.sleep(.2)
                subsports = sport.find_elements(By.CSS_SELECTOR, "ul > li")
                for subsport in subsports:
                    if "PROPS" not in subsport.text:
                        try:
                            subsport.find_element(By.CSS_SELECTOR, "a").click()
                        except:
                            pass

    def retrieveData(self):
        # TODO fix bs scraper
        self.driver.quit()
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        for event in self.soup.find_all(class_='panel panel-transparent'):
            try:
                eventType = event.find(class_='panel-title linesPanelTitle').text
                # TODO fix the string new line chraracters
                eventType.strip()
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
                except:
                    teamName = "NaN"
                try:
                    spread = row.find(class_='linesSpread').find('a').text
                except:
                    spread = "NaN"
                try:
                    odds = row.find(class_='linesMl').find('a').text
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


# Purewage All