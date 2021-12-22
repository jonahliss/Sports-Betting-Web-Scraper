import math
import time
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
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
        self.soup = ""
        self.allBets = {}

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
        self.driver.find_element(By.CSS_SELECTOR, "div[data-allow='BASKETBALL'] a").click()
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(1)
        # inserts the sport and league into the appropriate css locator
        enter_nfl = self.driver.find_elements(By.CSS_SELECTOR,
                                              "#{} > div > ul > li".format("FOOTBALL"))
        enter_nfl[0].find_element(By.CSS_SELECTOR, 'div').click()
        enter_nba = self.driver.find_elements(By.CSS_SELECTOR,
                                              "#{} > div > ul > li".format("BASKETBALL"))

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
        # TODO click the checkboxes for accordian headings basketball
        for checkbox in enter_nba:
            try:
                checkbox.find_element(By.CSS_SELECTOR, 'div').click()
            except:
                pass


    def retrieveData(self):
        time.sleep(4)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        for event in website.soup.select('div.page-lines > div')[:-2]:
            # tries to find the "header-a" tags that hold the event types
            try:
                eventType = event.find(class_='header-a').div.span.text
                # creates a new list eventType in the allBets dictionary, which will hold
                # dicts of the micro betting events
                website.allBets[eventType] = []
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

            else:
                for team in teams:
                    data = team.find_all('div', recursive=False)
                    try:
                        teamName = data[0].select('div.team > span')[0].text
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
            # append onto the list of events, the dict of the micro betting events
            website.allBets[eventType].append(tempEvent)

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
#%%

website = SportDynamic('https://www.sundaytilt.com/')
website.collectData()

#%%
while True:

    print('Starting')

    startingIndexCBB = 1200
    startingIndexNBA = 1200
    startingIndexCFB = 1200
    startingIndexNFL = 1200
    startingIndex = 1200
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
        elif ('ncaa' in bagOfWords or 'college' in bagOfWords) and 'football' in bagOfWords:
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
        worksheet.update(getRange(startingIndex - 5) + str(1), [[key], ["Sunday Tilt"]])
        worksheet.update(getRange(startingIndex - 4) + ':' + getRange(startingIndex - 1),
                         [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())

    print('Updated')

    time.sleep(30)

    website.driver.find_element(By.CSS_SELECTOR, "div[data-wager-type='REFRESH']").click()
