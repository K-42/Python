#! python3

import requests, bs4, datetime, time

#set default interval time between checks
DEFAULT_INTERVAL = 300

print ("  _  __  _  _     ____  ")
print (" | |/ / | || |   |___ \ ")
print (" | ' /  | || |_    __) |")
print (" | . \  |__   _|  / __/ ")
print (" |_|\_\    |_|   |_____|")
print ("")

url = requests.get('https://www.kickstarter.com/projects/coolminiornot/massive-darkness')
soup = bs4.BeautifulSoup(url.text, "html.parser")
backers = soup.select('span.pledge__backer-count')

print('Hello! This script checks whether any early backers have pulled out of the Massive Darkness kickstarter, potentially saving Ben the princely sum of 10 dollars.', end=' \n\n')
print("It'll run once every " + str(DEFAULT_INTERVAL) + " seconds. You can set a new interval value below or press enter to accept the default:")

#user can overwrite the default interval time if they desire
interval = input() 
interval = DEFAULT_INTERVAL if interval == '' else interval

print('OK!', end=' \n\n')   

print('Checking every ' +str(interval) + ' seconds. Current status:')
while True:
    if backers[0].getText() == '1,820 backers':
        print("I checked Massive Darkness at " + (str(datetime.datetime.now().time()))[:5]+ ". The slots for early backers were full.")
        time.sleep(int(interval))
    else:
        print("An early backer slot for Massive Darkness is available so I've sent you a text - act fast!")
        from twilio.rest import TwilioRestClient
        accountSID = ''
        authToken = ''
        twilioCli = TwilioRestClient(accountSID, authToken)
        myTwilioNumber = ''
        targetNumber = ''
        message = twilioCli.messages.create(body='Ben: an early backer has pulled out of Massive Darkness!', from_=myTwilioNumber, to=targetNumber)
        break
