import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def appendDataTeams(html_list, new_list):
    for item in html_list:
        team = item.text.split('\n')
        try:
            new_list.append(team[1])
        except:
            break


def appendDataSpreads(html_list, new_list):
    i = 0
    for item in html_list:
        if i % 2 == 0:
            array = item.text.split('\n')
            new_list.append(array[2])
        i += 1


def appendDataOdds(html_list, new_list):
    for item in html_list:
        array = item.text.split('\n')
        if len(array) == 3:
            new_list.append(array[1])


class SportDynamic:
    def __init__(self, url, sport, league):
        self.url = url
        self.sport = sport
        # TODO fix the static list positioning to be dynamic
        if league == "NCAAF":
            self.league = 16
        elif league == "NCAAB":
            self.league = 9
        else:
            self.league = 1
        self.teams_html = []
        self.spreads_html = []
        self.odds_html = []
        self.teams_list = []
        self.spreads_list = []
        self.odds_list = []
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def launchDriver(self):
        self.driver.get(self.url)
        time.sleep(1)

    def enterDriver(self):
        username = self.driver.find_element(By.NAME, "customerID")
        password = self.driver.find_element(By.NAME, "Password")
        username.send_keys("Gh75")
        password.send_keys("soccer1")
        self.driver.find_element(By.XPATH, '//button[text()="LOGIN"]').click()

    def navigateDriver(self):
        time.sleep(10)
        self.driver.find_element(By.CSS_SELECTOR, "div[data-allow='BASKETBALL'] a").click()
        time.sleep(1)
        # inserts the sport and league into the appropriate css locator
        enter_league = self.driver.find_element(By.CSS_SELECTOR,
                                                "#{} > div > ul li:nth-of-type({})".format(self.sport, self.league))
        enter_league.click()
        # button = self.driver.find_element(By.XPATH, '//span[text()="Continue"]')
        # button.click()

    def retrieveData(self):
        time.sleep(4)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        self.teams_html = soup.find_all(class_='team')
        self.spreads_html = soup.find_all(class_='line-play buy-skin')
        self.odds_html = soup.find_all(class_='line-play')

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
