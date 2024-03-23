import requests
from bs4 import BeautifulSoup
from cloudflare import run

def scrape(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements containing the text 'event' or similar
    event_elements = soup.find_all(lambda tag: tag.name == 'div' and 'event' in tag.text.lower())

    # Extract relevant information from each event element
    events = []
    for event in event_elements:
        title = event.find('h2').text.strip() if event.find('h2') else 'No Title'
        description = event.find('p').text.strip() if event.find('p') else 'No Description'
        # date = event.find('span', class_='date').text.strip() if event.find('span', class_='date') else 'No Date'
        events.append({'title': title, 'description': description})

    return events
