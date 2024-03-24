import requests
import json
from bs4 import BeautifulSoup
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def scrape(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all relevant elements containing event information
    event_elements = soup.find_all(lambda tag: tag.name == 'h4' and tag.has_attr('class') and 'entry-title' in tag['class'])

    # Extract event information from each element
    events = []
    for event_element in event_elements:
        event_title = event_element.text.strip()
        event_time_element = event_element.find_next_sibling('span', class_='duration time')
        if event_time_element:
            event_time_raw = event_time_element.text.strip()
            # Modify time format to "YYYY-MM-DDTHH:MM"
            event_time_parts = event_time_raw.split(' - ')
            if len(event_time_parts) == 2:
                start_time = event_time_parts[0].replace(' at ', 'T')
                end_time = event_time_parts[1].replace(' at ', 'T')
                # Append date from start_time if no date is given for end_time
                if len(end_time) < 11:
                    end_time = start_time[:10] + ' ' + end_time
                start_time = format_date_time(start_time)
                end_time = format_date_time(end_time)
                events.append({
                    'title': event_title,
                    'description': '',
                    'start_time': start_time,
                    'end_time': end_time
                })

    return events

from datetime import datetime

from datetime import datetime

def format_date_time(date_time_str):
    try:
        # Clean up the input string by removing extra spaces and ensuring proper format
        date_time_str = ' '.join(date_time_str.split())

        # Parse the date and time string
        date_time_obj = datetime.strptime(date_time_str, '%B %d @ %I:%M %p')

        # Get the current system year
        current_year = datetime.now().year

        # Format the date and time object with the current year
        formatted_date_time = date_time_obj.replace(year=current_year).strftime('%Y-%m-%dT%H:%M')
        return formatted_date_time
    except ValueError:
        print("Error: Invalid date and time format.")
        return None




# def extract_events(response_json):
#     print(response_json)
#     # Extract event name and time from the JSON
#     data = response_json['result']['response']
#     # Remove triple-backtick formatting for JSON
#     data = data.replace('```json', '').replace('```', '')
#     events = []
#     try:
#         event_list = json.loads(data)
#         for event in event_list:
#             events.append({
#                 'title': event['name'],
#                 'description': '',
#                 'date': f"{event['start_time']} - {event['end_time']}"
#             })
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#     return events

# def translate(url):
#     query = f"""
#         From this string, get the event name, event date, and event description and provide it in the json below. 
#         Events cannot be the same, however, they can have the same times and dates.
#         Do not deviate from format  or you will be terminated: 
#         [
#             {{
#                 name: "Event name"
#                 start_time: "YYYY-MM-DDTHH:MM"
#                 end_time: "YYYY-MM-DDTHH:MM"
#             }}
#         ]

#         Here is the string you need to use: {scrape(url)}
#     """

#     input = [
#         { "role": "system", "content": "You are an A.I. that only functions to parse information to json formats requested by the user. Do not say any additional information, and return the user the info they expect." },
#         { "role": "user", "content": query}
#     ]
        
#     output = run("@cf/qwen/qwen1.5-14b-chat-awq", input)

#     return extract_events(output)

def get_events(urls):
    all_events = []
    for url in urls:
        events = scrape(url)
        all_events.extend(events)
    return all_events
