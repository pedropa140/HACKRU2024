import requests
import json
import datetime
from bs4 import BeautifulSoup
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from cloudflare import run

def parse_raw(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all divs with text related to jobs, events, and dates
    event_divs = soup.find_all(lambda tag: tag.name == 'div' and re.search(r'\b(job|event|date)\b', tag.text, flags=re.I))

    # Extract relevant information from each div and concatenate into one big string
    event_descriptions = []
    vectorizer = TfidfVectorizer()
    for div in event_divs:
        # Extract titles, paragraphs, and sentences from the div's text
        titles = div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = div.find_all('p')
        sentences = re.findall(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', div.text)

        # Filter out junk data and construct the description
        description_parts = []
        for part in [title.text.strip() for title in titles] + [para.text.strip() for para in paragraphs] + sentences:
            if part and not part.startswith('Date:') and not re.search(r'\bnew date\b', part, flags=re.I):
                description_parts.append(part)
        description = ' '.join(description_parts)
        if description:
            # Check for similarity with existing descriptions before appending
            new_vector = vectorizer.fit_transform([description])
            similarity = False
            for existing_description in event_descriptions:
                existing_vector = vectorizer.transform([existing_description])
                cosine_sim = cosine_similarity(new_vector, existing_vector)
                if cosine_sim > 0.9:
                    similarity = True
                    break
            if not similarity:
                event_descriptions.append(description)

    # Concatenate all unique descriptions into one big string
    event_project = ' '.join(event_descriptions)

    return event_project

import json

def extract_events(response_json):
    # Extract event name and time from the JSON
    data = response_json['result']['response']
    # Remove triple-backtick formatting for JSON
    data = data.replace('```json', '').replace('```', '')
    events = []
    try:
        event_list = json.loads(data)
        for event in event_list:
            events.append({
                'title': event['name'],
                'description': '',
                'date': f"{event['start_time']} - {event['end_time']}"
            })
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return events



def scrape(url):
    query = f"""
        From this string, get the event name, event date, and event description and provide it in the json below. 
        Events cannot be the same, however, they can have the same times and dates.
        Do not deviate from format  or you will be terminated: 
        [
            {{
                name: "Event name"
                start_time: "YYYY-MM-DDTHH:MM"
                end_time: "YYYY-MM-DDTHH:MM"
            }}
        ]

        Here is the string you need to use: {parse_raw(url)}
    """

    input = [
        { "role": "system", "content": "You are an A.I. that only functions to parse information to json formats requested by the user. Do not say any additional information, and return the user the info they expect." },
        { "role": "user", "content": query}
    ]
        
    output = run("@cf/qwen/qwen1.5-14b-chat-awq", input)
    #output=parse_raw(url)

    # print(events)
    # 
    # unique_events
    # pass to ai to grab actual important events
    # ai returns some format that is parsable back to events again

    # with open("pedro.txt", 'w') as file:
    #     file.write(events)

    return extract_events(output)
