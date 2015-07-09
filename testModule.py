#from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


import sys,traceback

red="\033[01;33m{0}\033[00m"
green="\033[01;32m{0}\033[00m"
redon="\033[01;33m"
reset="\033[00m"


# @Todo Some of the code in here was learned over time and by trial-and-error
# so not everything has a real single consistent way of doing things.
# So I'll eventually work on some style and consistency points.
# Currently I'm pretty happy with the waitForLoad(driver) code.
# People say to avoid xpath expressions when possible.

# @Todo I should work on organizing this file into Classes.


MAX_WAIT=20
SHORT_WAIT=3

rolesFile=None

class TestCase:
    def __init__(self,name,description,function):
        self.name=name
        self.description=description
        self.function=function
        return
    
def go(tester):
    normalize(tester)
    for case in cases:
        if tester.text == case.name:
            case.function(tester)


def normalize(tester):
    try:
        tester.driver.switch_to.default_content()
    except:
        try:
            tester.driver.switch_to.alert.dismiss()
        except:
            tester.driver.switch_to.frame("contentFrame")
            tester.driver.switch_to.alert.dismiss()
        tester.driver.switch_to.default_content()
    return


def testLoggedIn(tester):
# It'd be good to check cookie expiration date here somehow.
    try:
        tester.driver.switch_to.default_content()
        # This is the social box in the upper right corner
        name_box = tester.driver.find_element_by_xpath("//a[@id='global-nav-link']")
        if name_box:
            return True
    except:
#        print redon,
#        traceback.print_exc()
#        print reset,
        return False
    return False

    
def tryLogin(tester):
    needLogin =not testLoggedIn(tester)
    if needLogin == False:
        return False
    print "Logging in"
#    tester.cookiesFile = "/tmp/cookies.pkl"
    tester.driver.get(tester.base)
#    tester.loadCookies()
    u = tester.driver.find_element_by_name("user_id")
    p = tester.driver.find_element_by_name("password")
    u.send_keys(tester.user)
    p.send_keys(tester.password)
    cu = tester.driver.current_url
    try:
        s = tester.driver.find_element_by_xpath("//input[@name='login']")
        s.click()
    except  Exception as e:
        print e,"submit not found"
        print redon,
        traceback.print_exc()
        print reset,
# @bug This should use something like waitForLoad(tester.driver)
    while tester.driver.current_url == cu:
        time.sleep(SHORT_WAIT)
        print tester.driver.current_url
    cu = tester.driver.current_url
#    if tester.cookiesFailed == False:
#        tester.saveCookies()
    print tester.driver.current_url
    return

# clickPage assumes the URL is going to change.
# it has a bit of problems on Blackboard with the frames/iframes
# this should be deprecated in lieu of .click() followed by waitForLoad
def clickPage(tester,link):
    cu = tester.driver.current_url
    try:
        link.click()
    except  Exception as e:
        print e,"bad link"
        print redon,
        traceback.print_exc()
        print reset,
    while tester.driver.current_url == cu:
        time.sleep(SHORT_WAIT)
        print tester.driver.current_url
    cu = tester.driver.current_url
    return

def setModuleProps(tester,name,roles):
    tryLogin(tester)
    tester.driver.switch_to.frame("navFrame")
    sysadmin = tester.driver.find_element_by_xpath("//span[text()[contains(.,'System Admin')]]")
    clickPage(tester,sysadmin)
#    tester.driver.switch_to.default_content()
    tester.driver.switch_to.frame("contentFrame")
    TandM = tester.driver.find_element_by_xpath("//a[text()[contains(.,'Tabs and Modules')]]")
    clickPage(tester,TandM)
    Modules=tester.driver.find_element_by_xpath("//a[text()[contains(.,'Modules')]]")
    clickPage(tester,Modules)
    PageButton=tester.driver.find_element_by_xpath("//a[text()[contains(.,'Edit Paging')]]")
    PageButton.click()
    IPP=tester.driver.find_element_by_xpath("//input[@id='listContainer_numResults']")
    IPP.clear()
    IPP.send_keys('500')
    Go = tester.driver.find_element_by_xpath("//a[@id='listContainer_gopaging']")
    Go.click()
    tester.driver.switch_to.default_content()
    tester.driver.switch_to.frame("contentFrame")
    Module = tester.driver.find_element_by_xpath("//a[text()[contains(.,\'"+name+"\')]]/following-sibling::span/a[@href='#contextMenu']") #
    Module.click()
    tester.driver.find_element_by_xpath("//a[text()[contains(.,'Edit Properties')]]").click()
    tester.driver.switch_to.default_content()
    tester.driver.switch_to.frame("contentFrame")
    tester.driver.find_element_by_xpath("//label[@for='availableChoiceSpecificRoles']").click()
    selectedAny=False
    for role in roles:
        selected=False
        method=0 # method 0 seems to be marginally faster if the window is tall enough
        if method==0:
            LeftSelect= tester.driver.find_element_by_xpath("//label[text()[contains(.,'Items to Select')]]/following-sibling::select")
            for opt in LeftSelect.find_elements_by_tag_name('option'):
                if opt.text.endswith(role):
                    opt.click()
                    selected=True
        elif method==1:
            LeftSelect= Select(tester.driver.find_element_by_xpath("//label[text()[contains(.,'Items to Select')]]/following-sibling::select"))
            for i, opt in enumerate(LeftSelect.options):
                if opt.text.endswith(role):
                    LeftSelect.select_by_visible_text(opt.text) # index(i)
                    selected=True
#        LeftSelect.select_by_visible_text("regexp:.*"+role)
        if selected:
            tester.driver.find_element_by_xpath("//button[@title='Move to list of selected items']").click()
            selectedAny=True
    if selectedAny:
        tester.driver.find_element_by_xpath("//input[@value='Submit']").click()
       
def sysadmin(tester):
    tryLogin(tester)
    tester.driver.switch_to.frame("navFrame")
    sysadmin = tester.driver.find_element_by_xpath("//span[text()[contains(.,'System Admin')]]")
    clickPage(tester,sysadmin)
    return

def module(tester):
    try: setModuleProps(tester,"USC Course Evaluations Response Rates",['Instructor','TA','Faculty'])
    except: pass
    try: setModuleProps(tester,"USC Student Course Evaluations",['Student'])
    except: pass
    try: setModuleProps(tester,"USC Course Evaluation Reports",['Instructor','TA','Faculty'])
    except: pass
    return

def setNumResults(d):
    "d is the driver"
    while onOnePage(d) is False:
        paging=WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.NAME,"openpaging")))
        paging.click()
        d.find_element_by_name("numResults").send_keys("5000")
        d.find_element_by_id("listContainer_gopaging").click()
        waitForLoad(d)
        d.switch_to.default_content()
        d.switch_to.frame("contentFrame")

def onOnePage(d):
    "The paging in Blackboard is super buggy in SP13"
    paging=WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.NAME,"openpaging")))
    count=d.find_element_by_id("listContainer_itemcount")
    counts = count.find_elements_by_tag_name("strong")
    if counts[1].text == counts [2].text:
#        print str(counts[1].text) +" of "+str(counts[2].text)
        return True
    return False
    

class pageIsReady(object):    
    def __init__(self):
        pass
    def __call__(self,d):
        return d.execute_script("return document.readyState") == "complete"

def waitForLoad(d):
    WebDriverWait(d,MAX_WAIT).until(pageIsReady())


def addInsitutionRoles(tester):
    sysadmin(tester)
    d=tester.driver
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    d.find_element_by_partial_link_text("Institution Roles").click()
    global rolesFile
    if not rolesFile:
        rolesFile = raw_input("Institution Roles File: ")
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    irFile = open(rolesFile,'r')
    for row in irFile :
        setNumResults(d)
        role = row.split(',')
        if len(role) != 2:
            continue
        name = role[0].replace('"','').lstrip()
        ID = role[1].replace('"','').rstrip().lstrip()
        try:
            # This doesn't work and I don't know why
            if d.find_element_by_xpath("//td[text()[contains(.,'"+ID+"')]]"):
                print ID+" found"
                continue
        except  Exception as e:
#            print e
#            for td in d.find_elements_by_tag_name('td'):
#                print td.text
#            print redon,
#            traceback.print_exc()
#            print reset,
            print "Creating "+ID
        WebDriverWait(tester.driver, MAX_WAIT).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Create Role"))).click()
#        d.find_element_by_partial_link_text("Create Role").click()
        d.switch_to.default_content()
        d.switch_to.frame("contentFrame")
        WebDriverWait(tester.driver, MAX_WAIT).until(EC.presence_of_element_located((By.ID,"roleLabel"))).send_keys(name)
        #d.find_element_by_id("roleLabel").
        d.find_element_by_id("roleId").send_keys(ID)
        try :
            d.find_element_by_name("top_Submit").click()
        except  Exception as e:
            print e,"bad link"
            print redon,
            traceback.print_exc()
            print reset,
        d.switch_to.default_content()
        d.switch_to.frame("contentFrame")
        try:
            error = d.find_element_by_id("inlineReceipt_bad").find_element_by_tag_name("li")
            d.find_element_by_name("top_Cancel").click()
            print error.text
        except  Exception as e:
            # print e
            # print redon,
            # traceback.print_exc()
            # print reset,
            pass
    return

def printTitle(d):
    try:
        print "Title: "+ d.find_element_by_tag_name("title").text    
    except:
        try:
            print "Title: "+d.current_url
        except:
            print "Title: None"

def delCourseContents(d):
    print "Deleting From Course"
    d.find_element_by_xpath("//th[text()[contains(.,'/courses')]]/span/a").click()
    d.find_element_by_partial_link_text("Open").click()
    WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.ID,"listContainer_selectAll"))).click()
    d.find_element_by_xpath("//label[text()[contains(.,'Recycle Bin')]]").click()
    print "Unselected recycle bin"
    d.find_element_by_partial_link_text("Delete").click()
    deleteAlert=WebDriverWait(d,MAX_WAIT).until(EC.alert_is_present())
    deleteAlert=tester.driver.switch_to.alert
    if deleteAlert:
        deleteAlert.accept()
    print "Pressed delete, this could take up to 10 minutes"
    # Super long delay
    try:
        WebDriverWait(d, 600).until(EC.presence_of_element_located((By.ID,"badMmsg1")))
        error=d.find_element_by_id('badMsg1').text
        print "Deleting from course: "+error
        if str(error).contains("Failure deleting content."):
            d.find_element_by_partial_link_text("Recycle Bin").click()
            print "Recursing into the recycle bin"
            delCourseContents(d)
    except:
        traceback.print_exc()
    print "Done deleting from course"
    return


def deleteOrphanedContent(tester,debug=True):
    sysadmin(tester)
    d=tester.driver
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    d.find_element_by_partial_link_text("Administrator Search").click()
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    WebDriverWait(tester.driver, MAX_WAIT).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Content Orphaned by Location"))).click()
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    if debug: 
        printTitle(d)
        print "About to edit paging"
    WebDriverWait(tester.driver, 300).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Edit Paging"))).click()
#    PageButton=d.find_element_by_xpath("//a[text()[contains(.,'Edit Paging')]]")
#    PageButton.click()
    IPP=d.find_element_by_xpath("//input[@id='listContainer_numResults']")
    IPP.clear()
    IPP.send_keys('1000')
    Go = d.find_element_by_xpath("//a[@id='listContainer_gopaging']")
    Go.click()
    for x in range(0,10):
        d.switch_to.default_content()
        d.switch_to.frame("contentFrame")
        if debug: 
            printTitle(d)
            print "Edited paging, waiting for selectAll"
        WebDriverWait(tester.driver, 600).until(EC.presence_of_element_located((By.ID,"listContainer_selectAll"))).click()
        error=None
        try:
            error=d.find_element_by_id('badMsg1').text
            print error
        except:
            pass
        try:
            if error and "Failure deleting content." in error:
                delCourseContents(d)
        except:
            traceback.print_exc()
        time.sleep(SHORT_WAIT)
        try:
            rows=d.find_element_by_id("listContainer_databody").find_elements_by_tag_name("TR")
            print str(len(rows))+" rows"
        except Exception as e:
            print "Failed at counting"
            traceback.print_exc()
        time.sleep(SHORT_WAIT)
        if debug: 
            printTitle(d)
            print "Select All Found"
        try:
            d.find_element_by_id('listContainer_row:0')
        except:
            print "Done"
            return False
        d.find_element_by_partial_link_text("Delete").click()
        if debug: print "Clicked Delete"
        time.sleep(SHORT_WAIT)
        deleteAlert=None
        try:
            deleteAlert=WebDriverWait(d,MAX_WAIT).until(EC.alert_is_present())
            deleteAlert=tester.driver.switch_to.alert
            if deleteAlert:
                deleteAlert.accept()
                
        except Exception as e:
            #print "Failed at alerts"
            #traceback.print_exc()
            pass
        print "Deleted 1000 courses"
    return True


def readystate_complete(d):
    return d.execute_script("return document.readyState") == "complete"

def deleteCourseUploads(tester,debug=True):
    sysadmin(tester)
    d=tester.driver
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    d.find_element_by_partial_link_text("Manage Content").click()
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    d.switch_to.frame("WFS_Navigation")
    WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Tools"))).click()
    WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Go to Location"))).click()
    d.switch_to.default_content()
    d.switch_to.frame("contentFrame")
    d.switch_to.frame("WFS_Files")
    Location = WebDriverWait(d, MAX_WAIT).until(EC.presence_of_element_located((By.ID,"entryURL_CSFile")))
    Location.click()
    Location.clear()
    Location.send_keys('/internal/courses/')
    d.find_element_by_xpath("//input[@name='top_Submit']").click()
    if debug: 
        printTitle(d)
        print "Searching to /internal/courses"
    WebDriverWait(d, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Edit Paging"))).click()
    IPP=d.find_element_by_xpath("//input[@id='listContainer_numResults']")
    IPP.clear()
    IPP.send_keys('2000')
    Go = d.find_element_by_xpath("//a[@id='listContainer_gopaging']")
    Go.click()
    sortedDesc=False
    while sortedDesc is False:
        size=WebDriverWait(d, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Size")))
        try:
            d.find_element_by_xpath("//span[@sortdir='down']")
            sortedDesc=True
            break
        except:
            size.click()
            time.sleep(2)

    irFile = open(tester.course_id_dump,'r')
    existingCourses={}
    for row in irFile :
        c=row.lstrip().rstrip()
        existingCourses[c]=True
    if len(existingCourses)<10:
        print "Problem with list of courses"
        return False
    if debug:
        print "Sample course ID: '" + list(existingCourses)[5] +"'"

    while True:
        WebDriverWait(d, 300).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Edit Paging")))
        time.sleep(2)
        d.find_element_by_id("listContainer_selectAll").click()
        time.sleep(4)
        rows=d.find_element_by_id("listContainer_databody").find_elements_by_tag_name("TR")
        clicked=len(rows)
        print "Found "+str(len(rows))+" rows"
        for row in rows:
            courseHREF = row.find_element_by_tag_name("th").find_element_by_tag_name("a")
            if courseHREF and courseHREF.text:
                if "20" in courseHREF.text:
                    courseName=courseHREF.text.lstrip().rstrip()
                    if debug:
                        print "Searching for course '"+courseName+"'"
                    if courseName not in existingCourses:
                        if debug: print "Checking course '"+courseName+"'"
                        continue
                if debug: print "Unchecking course '"+courseName+"'"
                row.find_element_by_tag_name('input').click()
                clicked-=1

        print "Will delete "+str(clicked)+" courses"
        d.find_element_by_partial_link_text("Delete").click()
        retries=0
        while retries<3:
            try:
                try:
                    deleteAlert=WebDriverWait(d,MAX_WAIT).until(EC.alert_is_present())
                except:
                    pass
                deleteAlert=d.switch_to.alert
                if deleteAlert:
                    time.sleep(3) # give me time to verify the alert is there
                    deleteAlert.accept()
                    break
            except Exception as e:
                print "Failed at alerts"
                traceback.print_exc()
                retries+=1
                time.sleep(3)

        if clicked==0:
            print "Done"
            return True
        time.sleep(30)
        WebDriverWait(d, 600).until(readystate_complete)
        print "Deleted "+str(clicked)+" courses"
        WebDriverWait(d, 300).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Refresh"))).click()
    return True


cases=[]
#               Case Name for the prompt, description, function to run
cases.append(TestCase("module","Assigns Roles to Modules",module))
cases.append(TestCase("login","Logs into Blackboard",tryLogin))
cases.append(TestCase("sysadmin","Goes to the system admin panel",sysadmin))
cases.append(TestCase("roles","Adds institution roles",addInsitutionRoles))
cases.append(TestCase("delOrphans","Deletes Orphaned Content",deleteOrphanedContent))
cases.append(TestCase("delUploads","Deletes Files from /internal/courses",deleteCourseUploads))

# @Todo: Maybe make an advanced breadcrum system that connects page tags with
# URL's with assertions so I don't have to start from the login page every time.
