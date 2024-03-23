# Standard Library Imports
import os
import sqlite3
from os import urandom
from dotenv import load_dotenv
import os.path

# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g
from datetime import datetime, timezone
import datetime as dt

# User Library Imports
from scraper import scrape
import cloudflare

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/ce787f621d3df59e07bd0ff342723ae1/ai/run/"
headers = {"Authorization": "Bearer wkd748PVSeSQRk2iQSS-eb8rB25ihto-296YmYAD"}

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
DATABASE = 'profiles.db'
app.config['DATABASE'] = DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))
    
@app.route("/")
def mainpage():
    return render_template("main.html")

@app.route("/edu")
def education():
    return render_template("education.html")
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        question_response = ("", "")

        return redirect("/edu")
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        passw = request.form.get("passw")
        print(email)
        print(passw)
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("error.html")

       
        if user[4] == passw:
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return render_template("error.html")

    return render_template("login.html")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        if not request.form.get("message"):
            return render_template("error.html")

        userInput = request.form.get("message")
        print("User Input:", userInput)
        query = f'The question the user wants to ask is {userInput}.'
        inputs = [
            { "role": "system", "content": "As a chatbot, your goal is to help with questions that only pertain into women in the field of STEM. Please answer the prompt not in markdown please." },
            { "role": "user", "content": query}
        ]
        result_dictionary = cloudflare.run("@cf/meta/llama-2-7b-chat-int8", inputs)
        print(result_dictionary['result'])
        result_result = result_dictionary['result']
        result_response = result_result['response']
        formatted_message = ""
        lines = result_response.text.split("\n")

        for line in lines:
            bold_text = ""
            while "**" in line:
                start_index = line.index("**")
                end_index = line.index("**", start_index + 2)
                bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                line = line[:start_index] + bold_text + line[end_index + 2:]
            formatted_message += line + "<br>"
        question_response = (userInput, formatted_message)

        print(question_response)

        return render_template("chatbot.html", question_response=question_response)
    else:
        question_response = ("", "")
        return render_template("chatbot.html", question_response=question_response)

@app.route('/events', methods=["GET", "POST"])
def prodev():
    if request.method == "POST":
        name = request.json.get('name')
        description = request.json.get('description')
        location = request.json.get('location')
        date = request.json.get('date')
        startTime = request.json.get('startTime')
        endTime = request.json.get('endTime')
        timezone = request.json.get('timezone')
        print(f'name {name}')
        print(f'Description: {description}')
        print(f'Location: {location}')
        print(f'Date: {date}')
        print(f'Start Time: {startTime}')
        print(f'End Time: {endTime}')
        print(f'Timezone: {timezone}')
        if name:
            # Process the event name as needed (e.g., save to database)
            print("Attending event:", name)
            return {"message": f"Attending event: {name}"}, 200
        else:
            return {"error": "Event name not provided in request body"},
    else:
       return render_template("events.html")

@app.route('/scrape-events')
def scrape_events():
    # URL of the website to scrape
    url = 'https://climateaction.rutgers.edu/'  # Replace with the actual URL of the website

    # Scrape events using the scrape() method
    events = scrape(url)

    # Render the scraped events using the scrape-events.html template
    return render_template('scrape-events.html', events=events)


init_db()
if __name__ == "__main__":
    app.run(debug=True)