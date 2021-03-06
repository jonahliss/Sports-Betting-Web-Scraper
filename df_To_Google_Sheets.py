import time
import gspread
import pandas as pd
import Draft_Kings_Web_Scraper as dkweb
import Sunday_Tilt_Web_Scraper as stweb
import Ubet_Web_Scraper as ubweb
import Wager_Wizard_Web_Scraper as wwweb
import Purewage_Web_Scraper as pwweb

# %%
# authorize user to connect to google sheet
# only needs to be done once
gc = gspread.service_account(filename='credentials.json')
print("Connected to Google Sheet")

# %%
sh = gc.open("BettingScraper")
worksheetNFL = sh.get_worksheet(2)
# sh.add_worksheet(title="Ubet", rows=1000, cols=2500)
worksheetCFB = sh.get_worksheet(3)
# sh.add_worksheet(title="NBA", rows=50, cols=10)
worksheetNBA = sh.get_worksheet(4)
# sh.add_worksheet(title="CBB", rows=100, cols=10)
worksheetCBB = sh.get_worksheet(5)

#%%
def getRange(index):
    if index / 26 >= 1:
        return chr(64 + (index // 26)) + chr(65 + (index % 26))
    return chr(65 + index)

# %%
# check if worksheet works
# print(worksheet.acell('A1').value)

worksheetNFL.clear()
worksheetCBB.clear()
worksheetNBA.clear()
worksheetCFB.clear()

#%%
website2 = ubweb.SportDynamic('https://ubet.ag/')
mapped = website2.collectData()

#%%
startingIndex = 0
for key in website2.allBets:
    print(key)
    ubdfNFL = website2.displayData(key)
    worksheetNFL.update(getRange(startingIndex) + ':' + getRange(startingIndex + 3),
                        [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())
    startingIndex += 4

#%%
while True:
    draftkings_classes = ['sportsbook-outcome-cell__line', 'sportsbook-odds american default-color',
                          'event-cell__name-text']


    # grab NFL worksheet

    # NFL = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561")
    # df = NFL.presentData()
    # worksheetNFL.update([df.columns.values.tolist()] + df.values.tolist())

    # website1 = stweb.SportDynamic('https://www.sundaytilt.com/')
    # website1.collectData()
    # stdfNFL = website1.displayData('NFL')
    # worksheetNFL.update('D1:', [stdfNFL.columns.values.tolist()] + stdfNFL.values.tolist())
    # stdfNBA = website1.displayData('NBA')
    # worksheetNFL.update('D1:', [stdfNBA.columns.values.tolist()] + stdfNBA.values.tolist())

    # NFL = pwweb.SportDynamic('https://ubet.ag/')
    # NFL.collectData()
    # ubdfNFL = NFL.displayData('NFL')
    # worksheetNFL.update('F:H', [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())
    #
    # # NFL = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"11,1\",this)\'")
    # # wwdfNFL = NFL.presentData()
    # # worksheetNFL.update('J:L', [wwdfNFL.columns.values.tolist()] + wwdfNFL.values.tolist())
    #
    # # # grab CFB worksheet
    # worksheetCFB.clear()
    # CFB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
    # dfCFB = CFB.presentData()
    # worksheetCFB.update([dfCFB.columns.values.tolist()] + dfCFB.values.tolist())
    #
    # # CFB = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NBA ')
    # # stdfCFB = CFB.presentData()
    # # worksheetCFB.update('D:F', [stdfCFB.columns.values.tolist()] + stdfCFB.values.tolist())
    #
    # CFB = ubweb.SportDynamic('https://ubet.ag/', 'NCAA FOOTBALL')
    # ubdfCFB = CFB.presentData()
    # worksheetCFB.update('F:H', [ubdfCFB.columns.values.tolist()] + ubdfCFB.values.tolist())
    #
    # # CFB = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"12,1\",this)\'")
    # # wwdfCFB = CFB.presentData()
    # # worksheetCFB.update('J:L', [wwdfCFB.columns.values.tolist()] + wwdfCFB.values.tolist())
    #
    # # grab NBA worksheet
    # worksheetNBA.clear()
    #
    # NBA = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
    # dfNBA = NBA.presentData()
    # worksheetNBA.update('A:C', [dfNBA.columns.values.tolist()] + dfNBA.values.tolist())
    #
    # # NBA = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"9,1\",this)\'")
    # # wwdfNBA = NBA.presentData()
    # # worksheetNBA.update('J:L', [wwdfNBA.columns.values.tolist()] + wwdfNBA.values.tolist())
    #
    # # grab CBB worksheet
    # worksheetCBB.clear()
    #
    # CBB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")
    # dfCBB = CBB.presentData()
    # worksheetCBB.update([dfCBB.columns.values.tolist()] + dfCBB.values.tolist())
    #
    # # CBB = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NCAA Basketball')
    # # stdfCBB = CBB.presentData()
    # # worksheetCBB.update('D1:', [stdfCBB.columns.values.tolist()] + stdfCBB.values.tolist())
    #
    # CBB = ubweb.SportDynamic('https://ubet.ag/', 'NCAA BASKETBALL - MEN')
    # ubdfCBB = CBB.presentData()
    # worksheetCBB.update('F:H', [ubdfCBB.columns.values.tolist()] + ubdfCBB.values.tolist())
    #
    # # CBB = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"10,1\",this)\'")
    # # wwdfCBB = CBB.presentData()
    # # worksheetCBB.update('J:L', [wwdfCBB.columns.values.tolist()] + wwdfCBB.values.tolist())
    #
    time.sleep(30)
