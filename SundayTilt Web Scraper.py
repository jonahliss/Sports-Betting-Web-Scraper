import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

sport = 'football'
league = 'NFL'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://www.sundaytilt.com/')
time.sleep(5) 

username = driver.find_element(By.NAME, "customerID")
password = driver.find_element(By.NAME, "Password")

username.send_keys("Gh75")
password.send_keys("soccer1")

login = driver.find_element(By.XPATH, '//button[text()="LOGIN"]')
login.click()

sport = driver.find_element(By.XPATH, '//span[text()="'+sport+'"]')
sport.click()

sport = driver.find_element(By.XPATH, '//span[text()="'+league+' "]')
sport.click()

button = driver.find_element(By.XPATH, '//span[text()="Continue"]')
button.click()

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

teams_html = soup.find_all(class_='team')
spreads_html = soup.find_all(class_='line-play buy-skin')
odds_html = soup.find_all(class_='line-play')

teams_list = []
for item in teams_html:
    team = item.text.split('\n')
    try:
        teams_list.append(team[1])
    except:
        break
        
spreads_list = []
i = 0
for item in spreads_html:
    if i % 2 == 0:
        array = item.text.split('\n')
        spreads_list.append(array[2])
    i += 1
    
odds_list = []
for item in odds_html:
    array = item.text.split('\n')
    if len(array) == 3:
        odds_list.append(array[1])
        
df = pd.DataFrame()
df = pd.concat([df, pd.DataFrame({'Teams':teams_list}),pd.DataFrame({'Spreads':spreads_list}),
                pd.DataFrame({'Odds':odds_list})], axis=1)
print(df)
