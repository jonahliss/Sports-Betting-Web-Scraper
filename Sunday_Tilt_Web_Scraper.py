import time
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
        for checkbox in enter_nba:
            try:
                checkbox.find_element(By.CSS_SELECTOR, 'div').click()
            except:
                pass
        # self.driver.find_element(By.CSS_SELECTOR, "#{} > div > ul > li > a".format(self.sport)).click()
        time.sleep(1)
        # button = self.driver.find_element(By.XPATH, '//span[text()="Continue"]')
        # button.click()

    def retrieveData(self):
        time.sleep(4)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")
        prevEvent = None
        for event in self.soup.select('div.page-lines'):
            print("Chris")
            print(event.get('data-group-line'))
            # if the data-group-attribute is different than the previous
            # event, then create a new eventType in the dictionary
            # if prevEvent.get('data-group-line', "") != event.get('data-group-line'):
            #     self.allBets[event.get('data-group-attribute')] = []
            # eventType = event.select()
            # prevEvent = event
        # print(self.soup)

    def presentData(self):
        self.launchDriver()
        self.enterDriver()
        self.navigateDriver()
        self.retrieveData()
        df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame({'Teams': self.teams_list}), pd.DataFrame({'Spreads': self.spreads_list}),
                        pd.DataFrame({'Odds': self.odds_list})], axis=1)
        df = df.fillna('')
        # return df

#%%
NFL = SportDynamic('https://www.sundaytilt.com/')

NFL.launchDriver()
NFL.enterDriver()
NFL.navigateDriver()

#%%
html = NFL.driver.page_source
NFL.soup = BeautifulSoup(html, "html.parser")

#%%
attr = ""
for event in NFL.soup.select('div.page-lines > div')[:-2]:
    # try to set attr to the attribute of the event
    # prevAttr will represent the previous attribute
    try:
        prevAttr = attr
        attr = event['data-group-line']
    # if no attribute of event is found, then
    # set attr to empty string
    except:
        attr = ""
        prevAttr = attr
    # if the data-group-attribute is different than the previous
    # event, then create a new list eventType in the dictionary,
    # which will hold dicts of micro betting events
    print(event.has_attr('class'))
    if attr != "":
        if prevAttr != attr or (not event.has_attr('class')):
            eventType = event.select('div.header-a > div > span')[0].text
            # print(eventType)
            # print("|||||||||||||||||||||||||||||||||||||")
        # NFL.allBets[attr] = []
# print(NFL.allBets)
