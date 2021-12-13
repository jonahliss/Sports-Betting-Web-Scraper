import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def appendDataTeams(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)


def appendDataSpreads(html_list, new_list):
    i = 0
    for item in html_list[1:]:
        if i % 3 == 0:
            new_list.append(item.text)
        i += 1


def appendDataOdds(html_list, new_list):
    i = 0
    for item in html_list[3:]:
        if i % 3 == 0:
            new_list.append(item.text)
        i += 1


class SportDynamic:
    def __init__(self, url, league):
        self.url = url
        self.league = league
        self.teams_html = []
        self.spreads_html = []
        self.odds_html = []
        self.teams_list = []
        self.spreads_list = []
        self.odds_list = []

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
        check_alls = self.driver.find_elements(By.CSS_SELECTOR, ".divLeagueContainer > a")
        for button in check_alls:
            if button.text == "Check All":
                button.click()
                time.sleep(.5)
        self.driver.find_element(By.ID, "continue-2").click()

    def retrieveData(self):
        html = self.driver.page_source
        # self.driver.quit()
        soup = BeautifulSoup(html, "html.parser")
        self.teams_html = soup.find_all(class_='text-black')
        self.spreads_html = soup.find_all(class_='btn btn-danger')
        self.odds_html = soup.find_all(class_='btn btn-danger')

    def sortData(self):
        appendDataTeams(self.teams_html, self.teams_list)
        appendDataSpreads(self.spreads_html, self.spreads_list)
        appendDataOdds(self.odds_html, self.odds_list)

    def presentData(self):
        self.launchDriver()
        self.enterDriver()
        self.navigateDriver()
        self.retrieveData()
        self.sortData()
        df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame({'Teams': self.teams_list}), pd.DataFrame({'Spreads': self.spreads_list}),
                        pd.DataFrame({'Odds': self.odds_list})], axis=1)
        df = df.fillna('')
        return df


# Ubet NFL
NFL = SportDynamic('https://ubet.ag/', 'NFL')
print(NFL.presentData())

'''

# Ubet CFB
CFB = SportDynamic('https://ubet.ag/', 'NCAA FOOTBALL')
CFB.launchDriver()
CFB.enterDriver()
CFB.navigateDriver()
CFB.retrieveData()
CFB.sortData()
CFB.presentData()

# Ubet NBA
NBA = SportDynamic('https://ubet.ag/', 'NBA')
NBA.launchDriver()
NBA.enterDriver()
NBA.navigateDriver()
NBA.retrieveData()
NBA.sortData()
NBA.presentData()

# Ubet CBB
CBB = SportDynamic('https://ubet.ag/', 'NCAA BASKETBALL - MEN')
CBB.launchDriver()
CBB.enterDriver()
CBB.navigateDriver()
CBB.retrieveData()
CBB.sortData()
CBB.presentData()
'''
