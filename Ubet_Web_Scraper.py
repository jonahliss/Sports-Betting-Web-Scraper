import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class SportDynamic:
    def __init__(self, url, league):
        self.url = url
        self.soup = ""
        self.league = league
        self.teams_html = []
        self.spreads_html = []
        self.odds_html = []
        self.teams_list = []
        self.spreads_list = []
        self.odds_list = []
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
        leagues.append(self.driver.find_element(By.CSS_SELECTOR, '#sport_IN-HOUSELIVEWAGERING'))
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
        self.driver.quit()
        self.soup = BeautifulSoup(html, "html.parser")

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
                try:
                    teamName = child.find_all('label')[0].text
                except:
                    teamName = "NaN"
                try:
                    spread = child.find_all('label')[1].text
                except:
                    spread = "NaN"
                try:
                    odds = child.find_all('label')[2].text
                except:
                    odds = "NaN"
                try:
                    moneyline = child.find_all('label')[3].text
                except:
                    moneyline = "NaN"

                bettingData["team"].append(teamName)
                bettingData["spread"].append(spread)
                bettingData["odds"].append(odds)
                bettingData["moneyline"].append(moneyline)

            # sets the betting data of the temporary event
            tempEvent[eventName.text] = bettingData

            # puts the event into the list of all events
            self.allBets[eventType].append(tempEvent)

    def presentData(self):
        self.launchDriver()
        self.enterDriver()
        self.navigateDriver()
        self.retrieveData()
        df = pd.DataFrame()
        # TODO make the dictionary parameter dynamic
        for event in self.allBets['NFL - 1ST HALF']:
            for item in event:
                df = pd.concat([df, pd.DataFrame({'Teams': event[item]['team'], 'Spreads': event[item]['spread'],
                                                  'Odds': event[item]['odds'],
                                                  'Moneyline': event[item]['moneyline']})], axis=0)
        df = df.fillna('')
        return df


# %%
# # Ubet NFL
NFL = SportDynamic('https://ubet.ag/', 'NFL')
print(NFL.presentData())
