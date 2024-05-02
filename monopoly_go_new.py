from botasaurus import *
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import date,datetime,timedelta
import json
import configparser
from pathlib import Path
import getpass
from crontab import CronTab

username = getpass.getuser()
print(f"username is {username}")
#load config
config = configparser.ConfigParser()
config.read('config.ini')
base_url = config["host"]["base_url"]
file_location = config["host"]["file_location"]
crontab_file= config["host"]["crontab"]
# Define today's date
today = date.today()

# Format the date as required
event_string = f"todays-events-{today.strftime('%b-%d-%Y').lower()}"
today_time_for_patch = today.strftime('%m/%d/%Y')


# Define the URL of the Monopoly Go events page
url = f"{base_url}{event_string}/"
print(url)
# use different Header

# declaration
@browser
def scrape_heading_task(driver: AntiDetectDriver, data):
    # Navigate to the Omkar Cloud website
    driver.get(url)
    
    # Retrieve the heading element's text
    heading = driver.text("h1")
    event_containers = driver.find_elements(By.CLASS_NAME, 'event-container')
    event_data = [container.text for container in event_containers]
    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        "heading": heading,
        "events" : event_data
    }

def loading_event_data():
    # load json
    f = open(file_location)
    data = json.load(f)
    events = []
    for event_string in data["events"]:
        # Split the string into lines
        lines = event_string.split('\n')
        # The first line is the title
        title = lines[0]
        # The second line is the time
        time = lines[1]
        # The third line, if present, is the duration
        duration = lines[2].replace('Duration: ', '') if len(lines) > 2 else None
        # Create a dictionary for the event
        event = {'Title': title, 'Time': time, 'Duration': duration}
        # Add the event to the list
        events.append(event)
    f.close()
    return events

def time_to_crontab(time_str):
    # Parse the input time string
    time_formats = ["%m/%d/%Y, %I:%M:%S %p"]
    dt = None
    if len(time_str.split(',')) == 1:
        today = datetime.today().strftime("%m/%d/%Y")
        time_str = f"{today}, {time_str}"
    for fmt in time_formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            pass

    if dt is None:
        return "Invalid time format"
    # Convert to crontab format
    dt += timedelta(hours=0)
    
    # Convert to crontab format
    minute = dt.minute
    hour = dt.hour
    day = dt.day
    month = dt.month
    
    cronData = f"{minute} {hour} {day} {month} *"
    return cronData


# Example usage
# input_time = "4/23/2024, 2:00:00 AM"
# crontab_result = time_to_crontab(input_time)
# print(f"Crontab expression for {input_time}: {crontab_result}")
def handling_event_data(events):
    print(events)
    my_cron = CronTab(user=username)
    remove_cron_jobs(my_cron)
    for event in events:
        Title="'{}'".format(event["Title"])
        Time="'{}'".format(event["Time"])
        Duration="'{}'".format(event["Duration"])
        command = f' cd /Users/kyle/Documents/projects/monopoly-go-events && /usr/local/bin/python3 ./text_message.py {Title} {Time} {Duration}'
        job = my_cron.new(command=command, comment='event_job')
        cron_expression = time_to_crontab(event["Time"].split("—")[0].strip())
        print(cron_expression)
        job.setall(cron_expression)
        my_cron.write()
    for job in my_cron:
        print(job)

def remove_cron_jobs(my_cron):
    my_cron.remove_all(comment='event_job')
    my_cron.write()


if __name__ == "__main__":
    # Initiate the web scraping task
    scrape_heading_task()
    # handling events data
    events = loading_event_data()
    handling_event_data(events)
