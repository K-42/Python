#! python3
#kickscraper.py is a multi-project early backer monitoring script for Kickstarter. It is set up to text an alert if any early backer slots become available for a given project.

import requests, bs4, datetime, time, configparser, os, json, re, sys, msvcrt, _thread

print ("  _  __  _  _     ____  ")
print (" | |/ / | || |   |___ \ ")
print (" | ' /  | || |_    __) |")
print (" | . \  |__   _|  / __/ ")
print (" |_|\_\    |_|   |_____|", end="\n\n")

i=0
while i < 21:
    print ('Kickscraper launched!'[i], end='')
    i += 1
    sys.stdout.flush()
    time.sleep(0.015)

print('\n')
  
#check for / load stored project information
if os.path.exists('./projectinfo.json'):
    with open('projectinfo.json') as f:
        projectdict = json.load(f)
else:
    projectdict = {}

#main menu
def menu():
    while True:
        if projectdict=={}:
            print ('\t[1] Add Project')
            print ('\t[2] Quit')
            try:            
                menuopt = int(input())
                if menuopt ==1:
                    newproject()
                else:
                    print('Bye bye!')
                    time.sleep(1)
                    sys.exit()
            except ValueError:
                print('Please enter a number.')
        else:
            print('\t[1] Track Projects')
            print('\t[2] Add Project')  
            print('\t[3] Delete Project')
            print('\t[4] Change Tracking Interval ' + '(' + str(interval) + ' seconds / project)')
            print('\t[5] Quit')
            try:            
                menuopt = int(input())
            except ValueError:
                print('Please enter a number.')
            if menuopt ==1:
                tracking_loop()
            elif menuopt ==2:
                newproject()
            elif menuopt ==3:
                delproject()
            elif menuopt ==4:
                setinterval()                
            elif menuopt ==5:
                print('Bye bye!')
                time.sleep(1)
                sys.exit()
            else:
                raise ValueError

#define and add project name / URL to dictionary, save to JSON
def newproject():
    urlcheck = re.compile(r'https://www.kickstarter.com/projects/\w*')
    while True:
        url = input('Enter the URL from the main page of the Kickstarter project: ')
        if urlcheck.match(url):
            projectname = (url.rsplit('?')[0]).rpartition('/')[-1]
            projectname = str.title(projectname.replace('-',' '))
            break
        else:
            print("That wasn't a valid URL.") #add a way back to menu       
    while True:
        print('The project is called \'' + projectname + '\'. Is that correct?')
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

#delete project details from dictionary and JSON
def delproject():
    while True:	
        n=0		
        print('Which project do you want to delete?')
        projectlist=[]
        for projects in sorted(projectdict):
            print('\t['+str(n+1)+'] ' + str.title(projects))
            projectlist.append(projects)            
            n+=1
            try:
                selection = int(input())
            except ValueError:
                    print('Enter the number of the project you want to delete.')
            if selection <= n:
                while True:
                    print("You're about to delete the details for '" + str.title(projectlist[selection-1]) + "'. Are you sure?")
                    print('\t[1] Yes')
                    print('\t[2] No')
                    try:
                        confirmation=int(input())
                        if int(confirmation) >2:
                            print('Please enter [1] or [2].')
                        elif confirmation==1:
                            print("'"+ (projectlist[selection-1]) + "' deleted.")
                            del(projectdict[(projectlist[selection-1])])
                            with open('projectinfo.json', 'w') as f:
                                json.dump(projectdict, f)
                            return
                        else:
                            return #breaks out of function! good tip.
                    except ValueError:
                        print('Please enter [1] or [2].')
            
config = configparser.RawConfigParser()

#read local Twilio variables
config.read('local.properties')

#set default interval time between checks
DEFAULT_INTERVAL = 60

#checks config file exists and either imports user definition or uses default interval
if os.path.exists('./config.ini'):
    config.read('config.ini')
    interval = config.get('application', 'interval')
else:
    interval = DEFAULT_INTERVAL #create file
    
#user can modify the interval
def setinterval():
    while True:
        print('Set number of seconds between each check:') 
        global interval
        interval = input()
        try:
            interval = int(interval) 
        except ValueError:
            print('What was that? Try a number.')
        config = configparser.RawConfigParser()
        config['application']={}
        config['application']['interval'] = str(interval)
        with open('config.ini', 'w') as file:
            config.write(file)            
        print('OK! ' + str(interval) + ' seconds is the new interval.', end=' \n\n')
        return

def quit_thread():
    while True:
        if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
            global loopswitch
            loopswitch='off'
            break
        else:
            continue

def tracking_loop():
    print("Checking projects. Press ESC to return to menu.")
    time.sleep(0.5)
    global loopswitch
    loopswitch = 'on'
    _thread.start_new_thread(quit_thread, ())
    while True:
        for projects in sorted(projectdict):
            url = projectdict[(projects)]
            pagescrape = requests.get(url)
            pageparse = bs4.BeautifulSoup(pagescrape.text, "html.parser")
            backers = pageparse.select('span.pledge__backer-count')
            if backers[0].getText() == '1,820 backers':
                print("I checked " + projects + " at " + (str(datetime.datetime.now().time()))[:5]+ ". The slots for early backers were full.")
                for t in range (60):
                    if loopswitch == 'on':
                        time.sleep(interval/len(projectdict)/60) #reduces loop completion time before return to menu. todo: make '60' dynamic so the user never waits more than 1 second even if they set a long interval.
                    else:
                        return                 
            else:
                print("An early backer slot for " + projects + " is available!")
                from twilio.rest import TwilioRestClient
                accountSID = config.get('twilio', 'accountSID')
                authToken = config.get('twilio', 'authToken')
                twilioCli = TwilioRestClient(accountSID, authToken)
                myTwilioNumber = config.get('twilio', 'phoneNumber')
                targetNumber = config.get('user', 'phoneNumber')
                message = twilioCli.messages.create(body=config.get('user', 'name') + ': an early backer has pulled out of ' + projects + '!', from_=myTwilioNumber, to=targetNumber)
                return

while True:
    menu()

#todo
#add twilio exception (e.g. no twilio detected, on screen prompt only)
#store new interval in config file
#make different pledges available and add these to project name e.g. Massive Darkness - Lightbringer Pledge
#make backers dynamic
#delete notified projects from dictionary and keep checking remainder

