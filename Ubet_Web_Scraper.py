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
            elif 'o' in temp or 'u' in temp:
                odds = temp
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
    key = key.replace("quarter", "q")
    key = key.replace("half", "h")
    key = key.replace("1st", "1")
    key = key.replace("2nd", "2")
    key = key.replace("3rd", "3")
    key = key.replace("4th", "4")
    key = key.replace("bk", "basketball")
    key = key.replace("b ", "basketball")
    key = key.replace("fb", "football")
    key = key.replace("(", "")
    key = key.replace(")", "")
    key = key.replace("-", "")
    key = key.replace(" ", "")
    key = key.replace("lines", "")
    key = key.replace("nan", "NaN")
    return key


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
            
            for child in children[1:-1]:
                determineChild(child)
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
        
#%%
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
    combinationDict = []

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
            dictEvent = {getRange(startingIndex - 5) + str(1), [[key], ["Sundaytilt"]]}
            combinationDict.append(dictEvent)
            dictEvent = {getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                             [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist()}
            combinationDict.append(dictEvent)
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
            
            dictEvent = {"range": getRange(startingIndex - 5) + str(1), "values": [[key], ["Ubet"]]}
            combinationDict.append(dictEvent)
            dictEvent = {"range": getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1), "values":
                             [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist()}
            combinationDict.append(dictEvent)

    worksheet.batch_update(combinationDict)
    print('Updated')
    
    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
    website.retrieveData()
    website.sortData()
