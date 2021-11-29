import mechanize
from bs4 import BeautifulSoup as bs

# br = mechanize.Browser()
# # may be illegal to bypass robots.txt
# br.set_handle_robots(False)
# br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
# br.open("https://ubet.ag")
#
# br.select_form(id='form1')
# br.form.set_all_readonly(False)
# br.form['Account'] = 'Efind1'
# br.form['Password'] = '123'
# print(br.form)
# response = br.submit('SubmitButtonControl')

# br = mechanize.Browser()
# # may be illegal to bypass robots.txt
# br.set_handle_robots(False)
# br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
# br.open("https://sundaytilt.com")
# print(br.title())
#
# br.select_form('client login')
# br.form.set_all_readonly(False)
# br.form['customerID'] = 'Gh75'
# br.form['Password'] = '123'
# print(br.form)
#
# response = br.submit()
#
# print(response.read())

br = mechanize.Browser()
# may be illegal to bypass robots.txt
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
res = br.open("https://www.betfastaction.ag/wager/Welcome.aspx")
print(res.read())

br.select_form(id='loginForm')
br.form.set_all_readonly(False)
br.form['account'] = 'Efindling2'
br.form['password'] = 'efindilng'
print(br.form)

response = br.submit()

print(response.read())
