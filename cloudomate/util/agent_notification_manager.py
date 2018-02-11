import smtplib
from smtplib import SMTPException
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from crontab import CronTab
import sys
import re
import subprocess


class AgentNotificationManager:

    extra_notification = None
    html_notification_content = "Not set"

    def __init__(self):
        pass

    def sendNotificationEmail(self,from_email = None,to_email = None):

        #some vpns block outgoing traffic to prevent spam abuse so start a smtpd service on a different port for 50 seconds (just to send the email)
        subprocess.Popen(['timeout', '20', 'python', '-m', 'smtpd', '-n', '-c', 'DebuggingServer', 'localhost:1025'])

        time.sleep(5)

        self.contentSetup()

        # sendfrom == my email address
        # sendto == recipient's email address
        sendfrom = "agentNotifier@bot.com"
        sendto = "pblank1234567.com"

        if from_email != None:
            sendfrom = from_email
        if to_email != None:
            sendto = to_email

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.getAgentIdentifier()
        msg['From'] = sendfrom
        msg['To'] = sendto
        content = MIMEText(self.html_notification_content, 'html')
        msg.attach(content)

        print("\nSending to: " + sendto)

        try:
            # Send the message via local SMTP server.
            s = smtplib.SMTP('localhost:1025')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(sendfrom, sendto, msg.as_string())
            s.quit()

            print("Successfully sent email")
            time.sleep(15)
        except SMTPException:
            print("Error: unable to send email")
        pass

    #retrieve the current ip address
    def getCurrentIpAdrress(self):
        c_ip = os.popen('curl ipv4bot.whatismyipaddress.com').read()
        return c_ip
        pass

    def getStartingIpAdress(self):
        #this file is set in setup.py
        starting_ip_file = os.path.expanduser("~") + '/.config/server-ip-address.txt'
        if os.path.isfile(starting_ip_file):
            file = open(starting_ip_file, "r")
            lines = file.readlines()
            file.close()
            return lines[0].replace('\n', '').replace('\r', '')
        else:
            return 'unknown'

    #retrieve the agent identifier
    def getAgentIdentifier(self):
        # this file is set in setup.py
        agent_id_file = os.path.expanduser("~") + '/.config/cloudomate_agent_id.txt'
        if os.path.isfile(agent_id_file):
            file = open(agent_id_file, "r")
            lines = file.readlines()
            file.close()
            return lines[0].replace('\n', '').replace('\r', '')
        else:
            return 'unknown'
        pass

    def getVpnIsActive(self):
        _ip = self.getStartingIpAdress()
        c_ip = self.getCurrentIpAdrress()
        if c_ip == _ip: return "False"
        return 'True'
        pass

    def getCurrentActiveVpnProvider(self):
        return 'UNKNOWN'
        pass

    def setBotExtraNotification(self,notification):
        self.extra_notification = notification
        pass

    def contentSetup(self):
        # Create the body of the message (in HTML version).
        html = """\<html><head></head><body>"""

        html += """\<h1>Your Bot giving an update</h1>"""
        html += "<h4><span style='color:green;'>" + self.getAgentIdentifier() + "</span> (bot's name) </h4>"
        html += "<h4><span style='color:green;'>" + self.getStartingIpAdress() + "</span> (ip address of server it is running on)</h4>"
        html += "<h4><span style='color:green;'>" + self.getCurrentIpAdrress() + "</span> (ip address trough wich traffic is being routed)</h4>"
        html += "<h4><span style='color:green;'>" + self.getVpnIsActive() + "</span> (wheter vpn is active)</h4>"
        html += "<h4><span style='color:green;'>" + self.getCurrentActiveVpnProvider() + "</span> (current active vpn provider)</h4>"

        if self.extra_notification == None:
            html += "<h4>No extra notification</h4>"
        else:
            html += "<h1 style='color:red;'>Extra Notification: </h1>"
            html += "<p>" + self.extra_notification + "</p>"
        html += """\</body></html>"""
        self.html_notification_content = html

    # use to validate email user-setting
    def isValidEmail(self, email):
       if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) == None:
           print("\n\nPlease make sure the email you provide is a valid email")
           exit(0)

    # add a crontab that mails the agent's status every x minutes
    def doNotifyEveryXMinutes(self,everyXminute=10,mailTo='pblank1234567@gmail.com'):
        #stop if the email provided is not a valid email
        self.isValidEmail(mailTo)

        #user based crontab
        cron_test = CronTab(True)

        #crontab executes this file with the arguments provided
        path_to_this_file = os.path.dirname(os.path.realpath(__file__))
        print(path_to_this_file)
        job_test = cron_test.new(command='python3 ' + path_to_this_file + ' ' + mailTo)

        #add comment to identify the crontab
        job_test.set_comment("notification-manager__ cloudomate notifier-agent")
        job_test.minute.every(everyXminute)

        #enable cronjob
        job_test.enable()
        if job_test.is_enabled():
            print("\ncron agent notifier active")
        cron_test.write()

    def turnOffAutoNotify(self):

        #userbased cron
        cron = CronTab(user=True)
        #remove all the cronjobs created by this script
        iter_test = cron.find_comment('notification-manager__ cloudomate notifier-agent')
        for test in iter_test:
            cron.remove(test)
        cron.write()
        print("\ncron agent notifier disabled")

    def autoNotifyIsOn(self):
        #userbased cron
        cron = CronTab(user=True)
        #if a job exists created by this script --> return true
        iter_test = cron.find_comment('notification-manager__ cloudomate notifier-agent')
        for test in iter_test:
            return True
        return False

if __name__ == '__main__':
    mailTo = 'pblank1234567@gmail.com'
    options_ = sys.argv
    if len(options_) > 1:
        print(options_[1])
        mailTo = options_[1]

    testNotification = AgentNotificationManager()
    testNotification.setBotExtraNotification("This was sent as a cron job")
    print("\nMailing to " + mailTo + "...")
    testNotification.sendNotificationEmail(to_email = mailTo)
