import smtplib, ssl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

#mail server credentials for sending automated e-mail
smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = ""  # example username@gmail.com
password = ""  # example emailpass01

#receiver email also can be used to mms message to user
receiver_email = ""  # example an email address or 1234567890@mms.att.net for mms message

#USCIS Case number that user will get notification for
caseNumber = ""

#function to send automated email or mms with the notification message
def notifyUser(notMessage):


    message = """\
    Subject: USCIS Status Update
    """
    message += notMessage

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        print("begin")
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    except Exception as e:
        # Prints any error messages to stdout
        print(e)
        return false
    finally:
        server.quit()
        return true

#Function to retrieve query result from the html node with Selenium WebDriver
#returns the case status
def getCaseCurrentStatus(caseNumber):

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    #path to chromedriver for Selenium
    chromedriver = "" # example C:/User/MyDesktop/Drivers/chromedriver.exe

    #web driver starts
    driver = webdriver.Chrome(chromedriver,options=chrome_options)
    #web drivers go to query page
    driver.get("https://egov.uscis.gov/casestatus/landing.do")
    #text box to input case number element is retrieved
    value = driver.find_element_by_id("receipt_number")
    #case number box is filled with case number
    driver.find_element_by_id("receipt_number").send_keys(caseNumber)
    #query sent
    driver.find_element_by_name("initCaseSearch").submit()

    #html node of desired result is retrieved from response page
    result = driver.find_element_by_class_name("rows.text-center").find_element_by_tag_name("h1").text

    driver.quit()
    return str(result)

def main():
    #initial case status variable
    caseStatus = ""
    #variable to keep last notifition date and it is used to send daily notification to user
    latestDailyNotificationDate = datetime.today().date()
    while 1:
        notificationMessage = ""

        #current status is retrieved from USCIS
        checkedCaseStatus = getCaseCurrentStatus(caseNumber)

        #if the current stored status of the case is different than the last query result status
        #an user message is created to send notification
        if(checkedCaseStatus != caseStatus):
            if(caseStatus == "" ):
                caseStatus = checkedCaseStatus
            else:
                notificationMessage = "Case Status is changed to " + checkedCaseStatus + "\n"
                caseStatus = checkedCaseStatus

        #if there is no change in status, there is no need to send notification
        if(notificationMessage != ""):
            notifyUser(notificationMessage)

        #once every morning after 4:00 am, user is notified with the latest status of the case
        if(datetime.today().date()>latestDailyNotificationDate):
            if(datetime.now().hour>4):
                dailyNotificationMessage = "Case Status:\n" + caseStatus
                notifyUser(dailyNotificationMessage)
                latestDailyNotificationDate = datetime.today().date()

        #In order to check status with reasonable interval, sleep timer is set 20 minutes
        time.sleep(1200)

if __name__ == "__main__":
    main()