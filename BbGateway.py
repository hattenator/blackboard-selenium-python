#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import signal,os
import testModule
import getpass
import traceback

DUMP_FILE='/usr/local/bbuser/archive/bbpilot_courses.csv'

class TestDriver:
    def __init__(self):
        try:
            environment=os.environ.get('BbEnvironment')
            BbWebCredentials=__import__("BbWebCredentials-"+environment)
            self.base = BbWebCredentials.server
            self.user = BbWebCredentials.user
            self.password=BbWebCredentials.password
        except Exception as  e:
            print str(e)
            environment=raw_input("Enter Environment (none/blackboard/uscprod/bbpilot/bb-test): ")
            try:
                BbWebCredentials=__import__("BbWebCredentials-"+environment)
                self.base = BbWebCredentials.server
                self.user = BbWebCredentials.user
                self.password=BbWebCredentials.password
            except:
                self.base=raw_input("Enter URL (https://blackboard.usc.edu): ")
                self.user=raw_input("Enter Username: ")
                self.password=getpass.getpass("Enter Password: ")
        self.fp=webdriver.FirefoxProfile()
#        self.fp.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0")
        self.fp.update_preferences()
        self.driver = webdriver.Firefox(self.fp)
        self.cookiesFailed = False
        self.taskTries=0
        self.driver.set_window_size(1400,900)
        self.course_id_dump=DUMP_FILE
        return

    def saveCookies(self):
        try:
            pickle.dump( self.driver.get_cookies() , open(self.cookiesFile,"wb"))
        except Exception as e:
            print e,"Couldn't save cookies"
        return

    def loadCookies(self):
        try:
            cookies = pickle.load(open(self.cookiesFile, "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as  e_sub:
                    print e_sub,cookie,"Couldn't load cookie.  current_url: ",self.driver.current_url
        except Exception as  e:
            print e,"Couldn't load cookies"
            self.cookiesFailed = True
        return

    def doPrompt(self):
        self.text = raw_input("Do Test? ")
        try:
            reload(testModule)
            testModule.go(self)
        except Exception as e:
            traceback.print_exc()
            print e,"Couldn't load test"
        return
    
testDriver = TestDriver()

def handler(signum,frame):
    testDriver.doPrompt()
    return

signal.signal(signal.SIGINT,handler)

print "Waiting for Signal"

while True:
    testDriver.doPrompt()
    time.sleep(1)

