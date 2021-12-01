import gspread
import pandas as pd
import Draft_Kings_Web_Scraper as dkweb
import Sunday_Tilt_Web_Scraper as stweb
import Ubet_Web_Scraper as ubweb

# authorize user to connect to google sheet
# only needs to be done once
gc = gspread.oauth(
    credentials_filename='./credentials.json',
    authorized_user_filename='./authorized_user.json'
)

sh = gc.open("BettingScraper")
worksheetNFL = sh.get_worksheet(0)
# sh.add_worksheet(title="CFB", rows=50, cols=10)
worksheetCFB = sh.get_worksheet(1)
# sh.add_worksheet(title="NBA", rows=50, cols=10)
worksheetNBA = sh.get_worksheet(2)
# sh.add_worksheet(title="CBB", rows=100, cols=10)
worksheetCBB = sh.get_worksheet(3)


# check if worksheet works
# print(worksheet.acell('A1').value)

draftkings_classes = ['sportsbook-outcome-cell__line','sportsbook-odds american default-color','event-cell__name-text']

NFL = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561", draftkings_classes)
NFL.retrieveData()
NFL.sortData()
df = NFL.presentData()
worksheetNFL.clear()
worksheetNFL.update([df.columns.values.tolist()] + df.values.tolist())

# # grab CFB worksheet
#
# CFB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775", draftkings_classes)
# CFB.retrieveData()
# CFB.sortData()
# dfCFB = CFB.presentData()
# worksheetCFB.clear()
# worksheetCFB.update([dfCFB.columns.values.tolist()] + dfCFB.values.tolist())

# grab NBA worksheet

# NBA = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846", draftkings_classes)
# NBA.retrieveData()
# NBA.sortData()
# dfNBA = NBA.presentData()
# worksheetNBA.clear()
# print([dfNBA.columns.values.tolist()] + dfNBA.values.tolist())
# worksheetNBA.update('D1:G50', [dfNBA.columns.values.tolist()] + dfNBA.values.tolist())

# grab CBB worksheet

# CBB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771", draftkings_classes)
# CBB.retrieveData()
# CBB.sortData()
# dfCBB = CBB.presentData()
# worksheetCBB.clear()
# worksheetCBB.update([dfCBB.columns.values.tolist()] + dfCBB.values.tolist())

# NFL = stweb.SportDynamic('https://www.sundaytilt.com/', 'football', 'NFL')
# NFL.launchDriver()
# NFL.enterDriver()
# NFL.navigateDriver()
# NFL.retrieveData()
# NFL.sortData()
# stdfNFL = NFL.presentData()

NCAA_Football = ubweb.SportDynamic('https://ubet.ag/', 'NCAA FOOTBALL')
sport = "NBA"
print('//span[text()=\"'+sport+'\"]')
