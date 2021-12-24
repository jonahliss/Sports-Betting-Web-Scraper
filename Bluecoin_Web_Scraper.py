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


# Function to standardize text formatting across websites
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
        # self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        self.allBets = {}
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
            
            teamName = "NaN"
            spread = "NaN"
            odds = "NaN"
            moneyline = "NaN"
            
            if len(tableRows) > 1:

                for row in tableRows:
                    cols = row.select('td')
                    # gets the eventID
                    try:
                        eventID = cols[2].text
                        teamName = cols[3].text
                    except:
                        # if eventID not found, it is not a valid event
                        continue
                        
                    for i in range(4, 7):
                        try:
                            temp = cols[i].text
                            if 'o' in temp or 'u' in temp:
                                odds = temp
                                odds = odds.replace("½", ".5")
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
                        bettingData["team"].append(formatKey(teamName))
                        bettingData["spread"].append(formatKey(spread))
                        bettingData["odds"].append(formatKey(odds))
                        bettingData["moneyline"].append(formatKey(moneyline))
                    # eventID has already been reached, so append the data onto list of all events
                    else:
                        isNew = True
                        bettingData["team"].append(formatKey(teamName))
                        bettingData["spread"].append(formatKey(spread))
                        bettingData["odds"].append(formatKey(odds))
                        bettingData["moneyline"].append(formatKey(moneyline))
                        tempEvent[eventName] = bettingData
                # append onto the list of events, the dict of the micro betting events
                self.allBets[eventType].append(tempEvent)

            else:  # iterate through the futures
                for row in tableFutureRows:
                    cols = row.select('td')
                    bettingData = {"team": [], "spread": [], "odds": [], "moneyline": []}
                    eventName = cols[4].text
                    teamName = cols[4].text
                    
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
        

# Establishing connection with Google Sheets
gc = gspread.service_account(filename='credentials.json')
sh = gc.open("BettingScraper")


# Determining sports and leageus to scrape
options = input('NCAA FOOTBALL, NBA, NFL\nWhat data do you want to scrape? ')


# Executing scraping process
website = SportDynamic('http://bluecoin.ag/core/mobile/', options)
website.collectData()

startTime = time.perf_counter() 

while True:
    
    print('Starting')

    startingIndexCBB = 2400
    startingIndexNBA = 2400
    startingIndexCFB = 2400
    startingIndexNFL = 2400
    startingIndex = 2400
    
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
        elif 'ncaa' in bagOfWords and ('football' in bagOfWords or 'fb' in bagOfWords):
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
            worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Bluecoin"]])
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
            
            worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Bluecoin"]])
            worksheet.update(getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                             [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())


    print('Updated')
    
    website.driver.find_element(By.NAME, "ctl00$WagerContent$ctl01").click()
    website.retrieveData()
    website.sortData()
