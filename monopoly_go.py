from botasaurus import *
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import date,datetime
import json
import configparser
 
#load config
config = configparser.ConfigParser()
config.read('config.ini')
base_url = config["host"]["base_url"]
file_location = config["host"]["file_location"]
# Define today's date
today = date.today()

# Format the date as required
event_string = f"todays-events-{today.strftime('%b-%d-%Y').lower()}"



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
    time_format = "%m/%d/%Y, %I:%M:%S %p"
    parsed_time = datetime.strptime(time_str, time_format)

    # Convert to crontab expression
    minute = parsed_time.minute
    hour = parsed_time.hour

    # Create the crontab expression
    crontab_expression = f"{minute} {hour}/3 * * *"

    return crontab_expression

# Example usage
# input_time = "4/23/2024, 2:00:00 AM"
# crontab_result = time_to_crontab(input_time)
# print(f"Crontab expression for {input_time}: {crontab_result}")
def handling_event_data(events):
    print(events)
    file_to_edit = "crontab"
    start_line_to_remove = "#monopoly"
    end_line_to_remove = "#monopoly_end"
    remove_between_lines(file_to_edit, start_line_to_remove, end_line_to_remove)
    for event in events:
        time_to_crontab(event["time"].split("—")[0].strip())


def remove_between_lines(filename, start_line, end_line):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Find the line numbers of the start and end lines
        start_index = None
        end_index = None
        for i, line in enumerate(lines):
            if line.strip() == start_line:
                start_index = i
            elif line.strip() == end_line:
                end_index = i

        # Remove lines between start and end (exclusive)
        if start_index is not None and end_index is not None:
            del lines[start_index + 1:end_index]

            # Write the modified content back to the file
            with open(filename, 'w') as file:
                file.writelines(lines)
            print(f"Content between '{start_line}' and '{end_line}' removed from {filename}")
        else:
            print(f"Lines '{start_line}' and '{end_line}' not found in {filename}")
    except FileNotFoundError:
        print(f"File {filename} not found")

if __name__ == "__main__":
    # Initiate the web scraping task
    #scrape_heading_task()
    # handling events data
    events = loading_event_data()
    handling_event_data(events)