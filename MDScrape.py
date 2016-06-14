import requests, bs4

print ("  _  __  _  _     ____  ")
print (" | |/ / | || |   |___ \ ")
print (" | ' /  | || |_    __) |")
print (" | . \  |__   _|  / __/ ")
print (" |_|\_\    |_|   |_____|")
print ("")

url = requests.get('https://www.kickstarter.com/projects/coolminiornot/massive-darkness')
soup = bs4.BeautifulSoup(url.text, "html.parser")
cheese = soup.select('span.pledge__backer-count')
  
if cheese[0].getText() == '1,820 backers':
    print("Early backers for Massive Darkness still at 1820. I'll text you if it drops.")
else:
    print("Early pledges for Massive Darkness are below maximum - I've sent a text: act fast!")
    from twilio.rest import TwilioRestClient
    accountSID = ''
    authToken = ''
    twilioCli = TwilioRestClient(accountSID, authToken)
    myTwilioNumber = ''
    targetNumber = ''
    message = twilioCli.messages.create(body='An early backer has pulled out of Massive Darkness!', from_=myTwilioNumber, to=targetNumber)
