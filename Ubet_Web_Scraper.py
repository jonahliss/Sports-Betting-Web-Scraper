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


# PURPOSE: removes all special chracters from the key
# PURPOSE: makes the key lowercase
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
    key = key.replace("nan", "NaN")
    return key


class SportDynamic:
    def __init__(self, url):
        self.url = url
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
        # leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_IN-HOUSELIVEWAGERING'))
        leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_COLLEGEBASKETBALL'))
        leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_FOOTBALL'))
        leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_COLLEGEFOOTBALL'))
        leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_BASKETBALL'))
        for button in leagues:
            button = button.find_element(By.CSS_SELECTOR, '.divLeagueContainer > a')
            if button.text == "Check All":
                button.click()
            if button.text == "Check All":
                button.click()

        self.driver.find_element(By.ID, "continue-2").click()

    def retrieveData(self):
        html = self.driver.page_source
        # self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        for event in self.soup.select('div.line'):
            eventType = event.select('h4')[0].text

            if not eventType in self.allBets:
                self.allBets[eventType] = []

            tempEvent = {}
            # gets the name of the event as a html tag
            eventName = event.select('div > div > h6')[0]
            tempEvent[eventName.text] = {}

            # gets the team and spreads of the event
            bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
            children = event.find_all('div', class_='row py-4')
            
            teamName = "NaN"
            spread = "NaN"
            odds = "NaN"
            moneyline = "NaN"
            
            for child in children[1:-1]:
                for i in range(4):
                    try:
                        temp = child.find_all('label')[i].text
                        
                        if temp == child.find_all('label')[0].text:
                            teamName = temp
                        elif 'o' in temp or 'u' in temp:
                            odds = temp
                            odds = odds.replace("½", ".5")
                        elif (temp.count('+') + temp.count('-')) == 2:
                            spread = temp
                        elif (temp.count('+') + temp.count('-')) == 1:
                            moneyline = temp
                    except:
                        pass

                bettingData["team"].append(formatKey(teamName))
                bettingData["spread"].append(formatKey(spread))
                bettingData["odds"].append(formatKey(odds))
                bettingData["moneyline"].append(formatKey(moneyline))

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


gc = gspread.service_account(filename='credentials.json')
sh = gc.open("BettingScraper")
print("Connected to Google Sheet")

website = SportDynamic('https://ubet.ag/')
website.collectData()

startTime = time.perf_counter() 


while True:
    
    print('Starting')

    startingIndexCBB = 1800
    startingIndexNBA = 1800
    startingIndexCFB = 1800
    startingIndexNFL = 1800
    startingIndex = 1800
    
    for key in website.allBets:
        ubdfNFL = website.displayData(key)
        key = formatKey(key)
        bagOfWords = key.split()
        if 'ncaa' in bagOfWords and 'basketball' in bagOfWords:
            print('NCAA Basketball')
            worksheet = sh.get_worksheet(1)
            worksheetNumber = 1
            startingIndexCBB += 5
            startingIndex = startingIndexCBB
        elif 'nba' in bagOfWords:
            print('NBA')
            worksheet = sh.get_worksheet(2)
            worksheetNumber = 2
            startingIndexNBA += 5
            startingIndex = startingIndexNBA
        elif 'ncaa' in bagOfWords and 'football' in bagOfWords:
            print('NCAA Football')
            worksheet = sh.get_worksheet(3)
            worksheetNumber = 3
            startingIndexCFB += 5
            startingIndex = startingIndexCFB
        elif 'nfl' in bagOfWords:
            print('NFL')
            worksheet = sh.get_worksheet(4)
            worksheetNumber = 4
            startingIndexNFL += 5
            startingIndex = startingIndexNFL
        else:
            continue
            
        try:
            worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Ubet"]])
            worksheet.update(getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                             [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())
        except:
            
            failTime = time.perf_counter()
            pause = 101 - (failTime - startTime)
            
            print('Pausing for', pause, 'seconds')
            time.sleep(pause)
            print('Resuming')
            
            gc = gspread.service_account(filename='credentials.json')
            sh = gc.open("BettingScraper")
            
            worksheet = sh.get_worksheet(worksheetNumber)
            
            startTime = time.perf_counter() 
            
            worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Ubet"]])
            worksheet.update(getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                             [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())


    print('Updated')
    
    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
    website.retrieveData()
    website.sortData()
