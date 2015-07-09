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
import sys
import os.path

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
        self.driver=webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)
#Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNIT.copy())
        self.cookiesFailed = False
        self.taskTries=0
        self.driver.set_window_size(1400,900)
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
testDriver.text="roles"
if len(sys.argv)>1 and os.path.isfile(sys.argv[1]) :
    print "Setting roles file to "+str(sys.argv[1])
    testModule.rolesFile=sys.argv[1]
    
testModule.go(testDriver)
