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
    for item in html_list:
        new_list.append(item.text.strip())


def appendDataOdds(html_list, new_list):
    i = 0
    for item in html_list:
        if i % 3 == 0:
            new_list.append(item.text)
        i += 1


class SportDynamic:
    def __init__(self, url):
        self.url = url
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
        self.driver.find_element(By.CSS_SELECTOR, "input[name='account']").send_keys("Efind")
        self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("blue67")
        self.driver.find_element(By.CSS_SELECTOR, ".btn_holder").click()

    def navigateDriver(self):
        time.sleep(1)
        # list of all elements of sport categories
        sports = self.driver.find_elements(By.CSS_SELECTOR, "#sportSide > li")
        for sport in sports:
            if sport.text != "SPORTS":
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
        html = self.driver.page_source
        self.driver.quit()
        soup = BeautifulSoup(html, "html.parser")
        self.teams_html = soup.find_all(class_='team_name')
        self.spreads_html = soup.find_all(class_='cboOdds cboLines')
        self.odds_html = soup.find_all(class_='RadComboBoxItem')

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


# Purewage All
NFL = SportDynamic('https://www.purewage.com/')
print(NFL.presentData())
