#! python3
#kickscraper.py is a multi-project early backer monitoring script for Kickstarter. It is set up to text an alert if any early backer slots become available for a given project.

import requests, bs4, datetime, time, configparser, os, json, re

print ("  _  __  _  _     ____  ")
print (" | |/ / | || |   |___ \ ")
print (" | ' /  | || |_    __) |")
print (" | . \  |__   _|  / __/ ")
print (" |_|\_\    |_|   |_____|", end="\n\n")

config = configparser.RawConfigParser()

#read script configuration file, read local configuration file
config.read('common.properties', 'local.properties') #todo workaround if files not in CWD

print('Kickscraper launched!', end=' \n\n')
  
#check for stored projects
if os.path.exists('./projectinfo.json'):
    with open('projectinfo.json') as f:
        projectdict = json.load(f)
else:
    projectdict = {}
    print("Looks like you haven't set up a project yet.", end=' ')
    
#project setup: check url input, give default project name w/ rename option, save to json 
def newproject():
    urlcheck = re.compile(r'https://www.kickstarter.com/projects/\w*')
    while True:
        url = input('Enter the URL from the main page of the Kickstarter project: ')
        if urlcheck.match(url):
            projectname = (url.rsplit('?')[0]).rpartition('/')[-1]
            projectname = projectname.replace('-',' ')
            break
        else:
            print("That wasn't a valid URL.")        
    while True:
        print('It\'s called \'' + projectname + '\'. Is that correct?')
        response = input('(Y/N): ')
        if str.lower(response) == 'yes' or str.lower(response) == 'y':
            projectdict[projectname]=url
            with open('projectinfo.json', 'w') as f:
                json.dump(projectdict, f)
            break
        elif str.lower(response) == 'no' or str.lower(response) == 'n':
            projectname = input('What do you want to call the project?:')
        else:
            print('Response not recognised. Please try again!')
			
#selection loop for stored projects (or start new project)			
while True:
    if projectdict=={}:
        newproject()
    else:
        n=0		
        print('Which project do you want to track?')
        projectlist=[]
        for projects in sorted(projectdict):
            print('['+str(n+1)+'] ' + str.title(projects))
            projectlist.append(projects)
            n+=1
        print('\n'+'['+str(n+1)+'] ' + 'Follow New Project')
        try:			
            selection = int(input())
            if selection <= n:
                global projectname
                projectname = projectlist[selection-1]
                url = projectdict[(projectlist[selection-1])]
                break
            else:
                newproject()
        except ValueError:
                print('Choose a number from the project list.')

#set default interval time between checks
DEFAULT_INTERVAL = 300

print("I'll check the " + projectname + " page once every " + str(DEFAULT_INTERVAL) + " seconds. You can set a new interval value below or press enter to accept the default:")

#user can overwrite the default interval time if they desire
interval = config.get('application', 'interval')
while True:
  interval = input()
  if interval !='':
    try:
      interval = int(interval)
      print('OK! ' + str(interval) + ' seconds is the new interval.', end=' \n\n')
      break
    except ValueError:
      print('What was that? Try a number.')
  else:
    interval = DEFAULT_INTERVAL
    break

print('Checking every ' +str(interval) + ' seconds. Current status:')

while True:
    pagescrape = requests.get(url)
    pageparse = bs4.BeautifulSoup(pagescrape.text, "html.parser")
    backers = pageparse.select('span.pledge__backer-count')
    if backers[0].getText() == '1,820 backers': #todo: make backer count dynamic
        print("I checked " + projectname + " at " + (str(datetime.datetime.now().time()))[:5]+ ". The slots for early backers were full.")
        time.sleep(int(interval))
    else:
        print("An early backer slot for " + projectname + " is available!")
        from twilio.rest import TwilioRestClient
        accountSID = config.get('twilio', 'accountSID')
        authToken = config.get('twilio', 'authToken')
        twilioCli = TwilioRestClient(accountSID, authToken)
        myTwilioNumber = config.get('twilio', 'phoneNumber')
        targetNumber = config.get('user', 'phoneNumber')
        message = twilioCli.messages.create(body=config.get('user', 'name') + ': an early backer has pulled out of ' + projectname + '!', from_=myTwilioNumber, to=targetNumber)
        break

#todo add loop break / return to menu
#todo add project deletion to menu
#todo add script quit to menu
