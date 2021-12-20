import time
import gspread
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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
        self.driver.find_element(By.NAME, "txtAccessOfCode").send_keys("dv50")
        self.driver.find_element(By.NAME, "txtAccessOfPassword").send_keys("efind")
        self.driver.find_element(By.XPATH, "//input[@value='login']").click()

    def navigateDriver(self):
        time.sleep(5)
        sports = website.driver.find_elements(By.CSS_SELECTOR, ".SportMenu_Div")
        for sport in sports:
            sportName = sport.find_element(By.TAG_NAME, "span").text
            if sportName == "Football" or sportName == "Basketball":
                time.sleep(.5)
                events = sport.find_elements(By.CSS_SELECTOR, "*")
                for event in events:
                    try:
                        event.click()
                    except:
                        pass

        website.driver.find_element(By.NAME, "ctl00$cphWorkArea$cmdContinue").click()

    def retrieveData(self):
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")

    def sortData(self):
        pass

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


# Wager Wizard NFL
gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

sh = gc.open("BettingScraper")
worksheet = sh.get_worksheet(6)
worksheet.clear()

#%%

website = SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx')
website.collectData()

