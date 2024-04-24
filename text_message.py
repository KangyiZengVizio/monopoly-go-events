import smtplib
import sys
 
import configparser
 
 
config = configparser.ConfigParser()
config.read('config.ini')

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
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
    # if len(sys.argv) < 4:
    #     print(f"Usage: python3 {sys.argv[0]} <PHONE_NUMBER> <CARRIER> <MESSAGE>")
    #     sys.exit(0)
 
    # phone_number = sys.argv[1]
    # carrier = sys.argv[2]
    # message = sys.argv[3]
    phone_number = config['recipient 2']['phone']
    carrier = config['recipient 2']['carrier']
    message = "This is a test!"
    send_message(phone_number, carrier, message)