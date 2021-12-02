import gspread
import pandas as pd
import Draft_Kings_Web_Scraper as dkweb
import Sunday_Tilt_Web_Scraper as stweb
import Ubet_Web_Scraper as ubweb
import Wager_Wizard_Web_Scraper as wwweb

# authorize user to connect to google sheet
# only needs to be done once
gc = gspread.oauth(
    credentials_filename='./credentials.json',
    authorized_user_filename='./authorized_user.json'
)

sh = gc.open("BettingScraper")
worksheetNFL = sh.get_worksheet(2)
# sh.add_worksheet(title="CFB", rows=50, cols=30)
worksheetCFB = sh.get_worksheet(3)
# sh.add_worksheet(title="NBA", rows=50, cols=10)
worksheetNBA = sh.get_worksheet(4)
# sh.add_worksheet(title="CBB", rows=100, cols=10)
worksheetCBB = sh.get_worksheet(5)


# check if worksheet works
# print(worksheet.acell('A1').value)

draftkings_classes = ['sportsbook-outcome-cell__line','sportsbook-odds american default-color','event-cell__name-text']

# grab NFL worksheet
worksheetNFL.clear()

NFL = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561")
df = NFL.presentData()
worksheetNFL.update([df.columns.values.tolist()] + df.values.tolist())

# NFL = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NBA ')
# stdfNFL = NFL.presentData()
# worksheetNFL.update('D1:', [stdfNFL.columns.values.tolist()] + stdfNFL.values.tolist())

NFL = ubweb.SportDynamic('https://ubet.ag/', 'NFL')
ubdfNFL = NFL.presentData()
worksheetNFL.update('D:F', [ubdfNFL.columns.values.tolist()] + ubdfNFL.values.tolist())

# NFL = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"11,1\",this)\'")
# wwdfNFL = NFL.presentData()
# worksheetNFL.update('J:L', [wwdfNFL.columns.values.tolist()] + wwdfNFL.values.tolist())

# # grab CFB worksheet
worksheetCFB.clear()
CFB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670775")
dfCFB = CFB.presentData()
worksheetCFB.update([dfCFB.columns.values.tolist()] + dfCFB.values.tolist())

# CFB = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NBA ')
# stdfCFB = CFB.presentData()
# worksheetCFB.update('D:F', [stdfCFB.columns.values.tolist()] + stdfCFB.values.tolist())

CFB = ubweb.SportDynamic('https://ubet.ag/', 'NCAA FOOTBALL')
ubdfCFB = CFB.presentData()
worksheetCFB.update('D:F', [ubdfCFB.columns.values.tolist()] + ubdfCFB.values.tolist())

# # TODO fix the static string param
# CFB = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"12,1\",this)\'")
# wwdfCFB = CFB.presentData()
# worksheetCFB.update('J:L', [wwdfCFB.columns.values.tolist()] + wwdfCFB.values.tolist())

# grab NBA worksheet
worksheetNBA.clear()

NBA = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670846")
dfNBA = NBA.presentData()
worksheetNBA.update('A:C', [dfNBA.columns.values.tolist()] + dfNBA.values.tolist())

# NBA = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NBA ')
# stdfNBA = NBA.presentData()
# worksheetNBA.update('D:F', [stdfNBA.columns.values.tolist()] + stdfNBA.values.tolist())

NBA = ubweb.SportDynamic('https://ubet.ag/', 'NBA')
ubdfNBA = NBA.presentData()
worksheetNBA.update('D:F', [ubdfNBA.columns.values.tolist()] + ubdfNBA.values.tolist())

# NBA = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"9,1\",this)\'")
# wwdfNBA = NBA.presentData()
# worksheetNBA.update('J:L', [wwdfNBA.columns.values.tolist()] + wwdfNBA.values.tolist())

# grab CBB worksheet
worksheetCBB.clear()

CBB = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/basketball/88670771")
dfCBB = CBB.presentData()
worksheetCBB.update([dfCBB.columns.values.tolist()] + dfCBB.values.tolist())

# CBB = stweb.SportDynamic('https://www.sundaytilt.com/', 'basketball', 'NCAA Basketball')
# stdfCBB = CBB.presentData()
# worksheetCBB.update('D1:', [stdfCBB.columns.values.tolist()] + stdfCBB.values.tolist())

CBB = ubweb.SportDynamic('https://ubet.ag/', 'NCAA BASKETBALL')
ubdfCBB = CBB.presentData()
worksheetCBB.update('D:F', [ubdfCBB.columns.values.tolist()] + ubdfCBB.values.tolist())

# CBB = wwweb.SportDynamic('https://www.wagerwizard.ag/Logins/007/sites/wagerwizard/index.aspx', "\'SportClick(\"10,1\",this)\'")
# wwdfCBB = CBB.presentData()
# worksheetCBB.update('J:L', [wwdfCBB.columns.values.tolist()] + wwdfCBB.values.tolist())
