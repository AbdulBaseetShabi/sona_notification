from bs4 import BeautifulSoup
from twill.commands import fv, submit, go, browser
import re
import logging
from pytz import timezone
import smtplib
from time import time, sleep
from email.message import EmailMessage
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import pymongo
from json import loads
from bson.json_util import dumps

class SonaNotification:

    def __init__(self):
        credentials = self.GetCredentials()
        self._username = credentials[0]
        self._password = credentials[1]
        self._email_username = credentials[2]
        self._email_password = credentials[3]
        connection_string = f"mongodb+srv://{credentials[4]}:{credentials[5]}@cluster0.cthkj.mongodb.net/{credentials[6]}?retryWrites=true&w=majority"
        self._db = pymongo.MongoClient(connection_string)
        self._collection = self._db.Sona.Studies

    def not_time_slot_label(self, label):
        return label and not re.compile("Timeslots Available").search(label)

    def checkNewSonaStudy(self):
        current_studies = []
        
        url = "https://wlu-ls.sona-systems.com/default.aspx"
        go(url)
        fv("2", "ctl00_ContentPlaceHolder1_userid", self._username)
        fv("2", "ctl00_ContentPlaceHolder1_pw", self._password)
        submit('0')

        url = 'https://wlu-ls.sona-systems.com/exp_info_participant.aspx'
        go(url)
        soup = BeautifulSoup(browser.html.strip(), "html.parser")
        for row in soup.findAll('tr')[1:]:
          td = BeautifulSoup(row.prettify(), "html.parser")
          for child in td.findAll('a', attrs={'class': False}):
            current_studies.append(child.string.lower().strip())

        old_studies = self.getOldStudies()
        differences, studies_not_displayed_anymore = self.compareList(current_studies, old_studies)

        # print("Old Studies: ", old_studies)
        # print("Current Studies on Sona: ", current_studies)
        # print("New Studies not done: ", differences)
        # print("Studies to delete: ", studies_not_displayed_anymore)

        if len(differences) != 0:
          for new_study in differences:
            self.sendEmail(new_study)
            self.updateDB(new_study)
            self.log("Email", "Old Studies: " + ", ".join(old_studies) + "; Current Studies: " + ", ".join(current_studies) + "; Differences: " + ", ".join(differences))
        self.deleteInDB(studies_not_displayed_anymore)
        return

    def getOldStudies(self):
        current_studies = []
        collection_data = self._collection.find({}, {'name': 1, '_id': 0})
        for study in loads(dumps(collection_data)):
          current_studies.append(study['name'])
        return current_studies

    def sendEmail(self, name_of_study):
        try:
            msg = EmailMessage()
            mailinglist = self.readFile("mailinglist.txt")
            msg.set_content(f"There is a new study called {name_of_study}. If you have already done it in the past please ignore this email.")
            msg['Subject'] = "New Sona Study Notification"
            msg['From'] = "donotreply@gmail.com"
            msg['To'] = ', '.join(mailinglist)
            self.log('Sending', "Sending Email...............")
            s = smtplib.SMTP_SSL('smtp.gmail.com')
            s.login(self._email_username, self._email_password)
            s.sendmail("donotreply@gmail.com", mailinglist, msg.as_string())
            s.quit()
        except Exception as a:
            print(a)

        return

    def updateDB(self, study):
        self._collection.insert_one({'name': study})
        return

    def deleteInDB(self, studies):
        for study in studies:
            self._collection.delete_one({'name': study})
        return 

    def compareList(self, newlist, oldlist):
        new_studies = []
        possibly_reopened_lateron = []

        #Sona Studies being displayed but not in DB
        for study in newlist:
            if study not in oldlist:
                new_studies.append(study)

        #Old studies that are not being displayed but can open later on
        for study_2 in oldlist:
            if study_2 not in newlist:
                possibly_reopened_lateron.append(study_2)
        return new_studies, possibly_reopened_lateron

    def readFile(self, file_name):
        response = []
        with open(file_name, "r") as file:
            for line in file:
                response.append(line.strip())
        file.close()
        return response

    def GetCredentials(self):
        return self.readFile("credentials.txt")

    def log(self, type, message):
        logging.basicConfig(handlers=[logging.StreamHandler()])
        log = logging.getLogger(type)
        log.info(message)
        return

def runThread():
    newInstance = SonaNotification()
    newInstance.checkNewSonaStudy()
    newInstance.log('Running', "Tick! The time is: %s" % datetime.now(timezone('US/Eastern')))

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(runThread, "interval", minutes=1)
    scheduler.start()