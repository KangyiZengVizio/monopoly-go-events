from botasaurus import *
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import date,datetime,timedelta
import json
import configparser
from pathlib import Path
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

    return f"{minute} {hour} {day} {month} *"


# Example usage
# input_time = "4/23/2024, 2:00:00 AM"
# crontab_result = time_to_crontab(input_time)
# print(f"Crontab expression for {input_time}: {crontab_result}")
def handling_event_data(events):
    print(events)
    file_to_edit = crontab_file
    start_line = "#monopoly"
    end_line = "#monopoly_end"
    inject_list_string=""
    remove_between_lines(file_to_edit, start_line, end_line)
    for event in events:
        crontab_expression = time_to_crontab(event["Time"].split("—")[0].strip())
        Title="'{}'".format(event["Title"])
        Time="'{}'".format(event["Time"])
        Duration="'{}'".format(event["Duration"])
        cwd=Path.cwd()
        inject_string=f"{crontab_expression} python3 {cwd}/text_message.py {Title} {Time} {Duration} \n"
        inject_list_string+=inject_string
    print(inject_list_string)
    inject_string_to_crontab(file_to_edit,start_line, end_line, inject_list_string)


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

def inject_string_to_crontab(file_path, start_line, end_line,string_to_inject):
    try:
        # Read the content of the file
        with open(file_path, 'r',encoding='utf-8') as f:
            lines = f.readlines()

        # Find the indices of the lines containing "#monopoly" and "#monopoly_end"
        start_index = None
        end_index = None
        for i, line in enumerate(lines):
            if line.strip() == start_line:
                start_index = i
            elif line.strip() == end_line:
                end_index = i

        # If both indices are found, inject the string between them
        if start_index is not None and end_index is not None:
            lines.insert(end_index, string_to_inject + '\n')

            # Write the modified content back to the file
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print(f"String injected successfully between lines #monopoly and #monopoly_end.")
        else:
            print("Error: Could not find the specified lines in the file.")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")


if __name__ == "__main__":
    # Initiate the web scraping task
    #scrape_heading_task()
    # handling events data
    events = loading_event_data()
    handling_event_data(events)