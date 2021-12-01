import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

NFL = "\'SportClick(\"11,1\",this)\'"
NCAA_Football = "\'SportClick(\"12,1\",this)\'"
NBA = "\'SportClick(\"9,1\",this)\'"
NCAA_Basketball = "\'SportClick(\"10,1\",this)\'"


def appendDataTeams(html_list, new_list):
    for item in html_list:
        new_list.append(item.text)


def appendDataSpreads(html_list, new_list):
    for item in html_list:
        new_list.append(item.text.strip())


def appendDataOdds(html_list, new_list):
    i = 0
    for item in html_list:
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
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(self.url)

    def enterDriver(self):
        self.driver.find_element(By.NAME, "txtAccessOfCode").send_keys("dv50")
        self.driver.find_element(By.NAME, "txtAccessOfPassword").send_keys("efind")
        self.driver.find_element(By.XPATH, "//input[@value='login']").click()

    def navigateDriver(self):
        self.driver.find_element(By.XPATH, "//div[@onclick=" + self.league + "]").click()
        self.driver.find_element(By.CLASS_NAME, "bottomContinue").click()

    def retrieveData(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        self.teams_html = soup.find_all(class_='team_name')
        self.spreads_html = soup.find_all(class_='cboOdds cboLines')
        self.odds_html = soup.find_all(class_='RadComboBoxItem')

    def sortData(self):
        appendDataTeams(self.teams_html, self.teams_list)
        appendDataSpreads(self.spreads_html, self.spreads_list)
        appendDataOdds(self.odds_html, self.odds_list)

    def presentData(self):
        df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame({'Teams': self.teams_list}), pd.DataFrame({'Spreads': self.spreads_list}),
                        pd.DataFrame({'Odds': self.odds_list})], axis=1)
        return self.df


NBA = SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', NCAA_Basketball)
NBA.launchDriver()
NBA.enterDriver()
NBA.navigateDriver()
NBA.retrieveData()
NBA.sortData()
NBA.presentData()
