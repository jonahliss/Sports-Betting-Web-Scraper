import gspread
import pandas as pd
import Draft_Kings_Webscraper as dkweb

# authorize user to connect to google sheet
# only needs to be done once
gc = gspread.oauth(
    credentials_filename='./credentials.json',
    authorized_user_filename='./authorized_user.json'
)

sh = gc.open("BettingScraper")
worksheet = sh.get_worksheet(0)

print(worksheet.acell('A1').value)

draftkings_classes = ['sportsbook-outcome-cell__line','sportsbook-odds american default-color','event-cell__name-text']
NFL = dkweb.SportStatic("https://sportsbook.draftkings.com/leagues/football/88670561", draftkings_classes)
NFL.retrieveData()
NFL.sortData()
df = NFL.presentData()

worksheet.update([df.columns.values.tolist()] + df.values.tolist())
