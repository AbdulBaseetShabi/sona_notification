from bs4 import BeautifulSoup
from twill.commands import fv, submit, go, browser
import re
import smtplib
from time import time, sleep
from email.message import EmailMessage
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

class SonaNotification:

    def __init__(self):
      credentials = self.GetCredentials()
      self._username = credentials[0]
      self._password = credentials[1]
      self._email_username = credentials[2]
      self._email_password = credentials[3]

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

      differences = self.compareList(current_studies, self.readFile("old_studies.txt"))

      if len(differences) != 0:
        for new_study in differences:
          self.sendEmail(new_study)
          self.updateFile(new_study)
      return

    def sendEmail(self, name_of_study):
      try:
        msg = EmailMessage()
        msg.set_content(f"There is a new study called {name_of_study}. If you have already done it in the past please ignore this email.")
        msg['Subject'] = "New Sona Study Notification"
        msg['From'] = "donotreply@gmail.com"
        msg['To'] = self.readFile("mailinglist.txt")
        print("Sending Email...............")
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        s.login(self._email_username, self._email_password)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
      except Exception as a:
        print(a)

      return

    def updateFile(self,study):
      with open("old_studies.txt", "a") as file:
        file.write(study + "\n")
      file.close()
      return

    def compareList(self, newlist, oldlist):
      return [x for x in newlist if x not in oldlist]

    def readFile(self, file_name):
      response = []
      with open(file_name, "r") as file:
        for line in file:
          response.append(line.strip())
      file.close()
      return response

    def GetCredentials(self):
      return self.readFile("credentials.txt")
      
def runThread():
  newInstance = SonaNotification()
  newInstance.checkNewSonaStudy()
  print("Cron job is running")
  print("Tick! The time is: %s" % datetime.now())

if __name__ == "__main__":  
  scheduler = BlockingScheduler()
  scheduler.add_job(runThread, "interval", minutes=2)
  scheduler.start()