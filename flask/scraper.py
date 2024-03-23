import requests
import json
import datetime
from bs4 import BeautifulSoup
from cloudflare import run
import re

def scrape(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all divs with text related to jobs, events, and dates
    event_divs = soup.find_all(lambda tag: tag.name == 'div' and re.search(r'\b(job|event|date)\b', tag.text, flags=re.I))

    # event_divs = 

    # Use a set to store unique descriptions
    unique_descriptions = set()

    # Extract relevant information from each div
    
    events = []

    query = f"""
        From this string, get the event date, event name, and event description and give it to me in this exact format: 
        
        Event Name: "Event name"
        Event Start Time: "YYYY-MM-DDTHH:MM"
        Event End Time: "YYYY-MM-DDTHH:MM"

        Here is the string you need to use:
    """

    input = [
        { "role": "system", "content": "You are a friendly assistant that helps write stories" },
        { "role": "user", "content": query}
    ]

    count = 1

    for div in event_divs:
        # Extract titles, paragraphs, and sentences from the div's text
        titles = div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = div.find_all('p')
        sentences = re.findall(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', div.text)

        # Concatenate titles, paragraphs, and sentences into a single description
        description = ' '.join([title.text.strip() for title in titles] + [para.text.strip() for para in paragraphs] + sentences)


        # Check if the description is unique
        if description not in unique_descriptions:
            unique_descriptions.add(description)
            # Add the event to the events list
            input[1]["content"] += "Description" + str(count) + ": " + description
            count += 1
        
            # events.append({'description': input[1]["content"]})

        
    output = run("@cf/meta/llama-2-7b-chat-fp16", input)


    
    # print(events)
    # 
    # unique_events
    # pass to ai to grab actual important events
    # ai returns some format that is parsable back to events again

    # with open("pedro.txt", 'w') as file:
    #     file.write(events)

    return events
