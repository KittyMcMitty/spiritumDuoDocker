#!/usr/bin/python

import sys
import os
sys.path += [os.path.abspath('/src/libraries')]

from commonFunctions import singleInstance, logAndError, tee
from datetime import datetime
import pexpect 
#from pexpect import popen_spawn
from inspect import currentframe as CF # help with logging
from inspect import getframeinfo as GFI # help with logging
import threading
import time as t



# Make sure only one instance of this program is running
single , fp = singleInstance()
if not single:
    sys.exit(1)


# Determine where main program files are stored
directory = os.path.dirname(os.path.realpath(__file__))



# Error and log handling
exitFlag = [0]
errMode = 'pf' # p = print to screen, f = print to file,  e = end program
errorFileAddress = f'{ directory }/startUp.err'
outputlog = open(errorFileAddress, "a")
sys.stderr = tee(sys.stderr, outputlog)
logFileAddress = f'{ directory }/startUp.log'
logMode = 'pf' # p = print to screen, f = print to file, u = restart program on code update


# Use 1st given argument as log mode, 2nd as error mode
try:
	logMode = sys.argv[1]
	errMode = sys.argv[2]
except:
	pass
msg = logAndError(errorFileAddress, logFileAddress, errMode, logMode)



# Main threading code
class mainThreadClass(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		PIDMessage = 'Start up program started: %s'%os.getpid()
		msg.log(PIDMessage)
		mainThread()
		msg.log('Thread: main exited')



def mainThread():
    #  production,  development, basic
    runMode = os.getenv('runMode')
    #runMode = 'basic'
    manageLocation = '/src/web/'
    msg.log(f'Docker start up mode: { runMode }')


    commands = [
        'ln -s /etc/nginx/sites-available/spiritumDuo.conf /etc/nginx/sites-enabled/'
    ]

    if runMode == 'initialise':
        commands.append(f'python { manageLocation }manage.py makemigrations')
        commands.append(f'python { manageLocation }manage.py migrate')
        commands.append(f'python { manageLocation }manage.py createsuperuser --noinput')
        #commands.append(f'python { manageLocation }manage.py loaddata GHNHSFT_initialData.json')
    elif runMode == 'production':
        commands.append('/etc/init.d/nginx restart')
        commands.append('uwsgi --emperor /etc/uwsgi/vassals')
    elif runMode == 'development':
        commands.append('python /src/web/manage.py runserver 0.0.0.0:8080')

    for c in commands:
        childUpdate = pexpect.spawn(c, timeout = None)
        msg.log(childUpdate.read())

    #for x in commands:
    #    os.system(x)

    return



# Loop threading code
class loopThreadClass(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		loopThread()
		msg.log('Thread: loop exited\n')



def loopThread():
    msg.log(f'Thread: loop running...')
    while exitFlag[0] == 0:
        t.sleep(10)


if __name__ == '__main__':
    # Create new threads
    threadMain = mainThreadClass()
    threadLoop = loopThreadClass()
    # Start new Threads
    threadMain.start()
    threadLoop.start()
