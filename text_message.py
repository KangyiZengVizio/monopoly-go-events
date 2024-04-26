import smtplib
import sys
import configparser
 
print(sys.argv)

Title=sys.argv[1]
Time=sys.argv[2]
Duration=sys.argv[3]

config = configparser.ConfigParser()
config.read('config.ini')

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com",
    "gmail": "@gmail.com"
}
 
EMAIL = config["sender"]["email"]
PASSWORD = config["sender"]["password"]
 
def send_message(phone_number, carrier, message):
    
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)
    print(recipient)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    #server.set_debuglevel(True)
    server.ehlo()
    server.starttls()
    server.login(auth[0], auth[1])
    server.sendmail(auth[0], recipient, message)
    server.quit()
 
 
if __name__ == "__main__":

    recipient_1 = config['recipient 1']
    recipient_2 = config['recipient 2']
    recipients=[recipient_1,recipient_2]
    message = f"\nEvent {Title} will begin, At {Time},duration is {Duration}".encode('utf-8')
    print(message)
    for re in recipients:
        send_message(re['phone'], re['carrier'], message)
    
    #send_message(phone_number, carrier, message1)
    