import requests
from bs4 import BeautifulSoup
from cloudflare import run
import re

def scrape(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all divs with text related to jobs, events, and dates
    event_divs = soup.find_all(lambda tag: tag.name == 'div' and re.search(r'\b(job|event|date)\b', tag.text, flags=re.I))

    # Use a set to store unique descriptions
    unique_descriptions = set()

    # Extract relevant information from each div
    events = []
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
            events.append({'description': description})

        # unique_events
        # pass to ai to grab actual important events
        # ai returns some format that is parsable back to events again
        
    return events
