import gspread
import pandas as pd
import Dra

# authorize user to connect to google sheet
# only needs to be done once
gc = gspread.oauth(
    credentials_filename='./credentials.json',
    authorized_user_filename='./authorized_user.json'
)

sh = gc.open("BettingScraper")
worksheet = sh.get_worksheet(0)

print(worksheet.acell('A1').value)

d = {'col1': [1, 10], 'col2': [3, 4]}
df = pd.DataFrame(data=d)

worksheet.update([df.columns.values.tolist()] + df.values.tolist())
