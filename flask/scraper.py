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
