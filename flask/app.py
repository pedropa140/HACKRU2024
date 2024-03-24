# Standard Library Imports
import os
import sqlite3
from os import urandom
from dotenv import load_dotenv
import os.path
import json

# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from datetime import datetime, timezone
import datetime as dt

import cloudflare
from authlib.integrations.flask_client import OAuth
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError
SCOPES = ['https://www.googleapis.com/auth/calendar']

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/ce787f621d3df59e07bd0ff342723ae1/ai/run/"
headers = {"Authorization": "Bearer wkd748PVSeSQRk2iQSS-eb8rB25ihto-296YmYAD"}

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
DATABASE = 'profiles.db'
app.config['DATABASE'] = DATABASE

oauth = OAuth(app)
oauth.register(
    "oauthApp",
    client_id='GSlRU8ssqQmC7BteFwhCLqxonlmtvSBP',
    client_secret='4YFxFjzvuXtXyYMoJ9coyCHDphXdUYMAGNF3gcwpZh16Hv-Hz_s83TqawI0RmR2b',
    api_base_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com',
    access_token_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/token',
    authorize_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/authorize',
    client_kwargs={'scope': 'scope_required_by_provider'}
)


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

from flask import redirect, url_for, session

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

    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True))

@app.route('/authorized')
def authorized():
    # token = oauth.oauthApp.
    # oauth_token = token['access_token']
    # session['oauth_token'] = oauth_token
    # token = {
    #     "token": session['oauth_token']
    # }
    # with open('token.json', 'w') as file:
    #     file.write(json.dumps(token))
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if os.path.exists("token.json"):
                    os.remove("token.json")
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    return redirect(url_for('chatbot'))

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
        lines = result_response.split("\n")

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

def generate_scheduling_query(tasks):
    
    current_time = datetime.now()

    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    print(current_time_str)
    query = "Today is " + current_time_str + "\n"
    query += """
    As an AI, your task is to generate raw parameters for creating a quick Google Calendar event. Your goal is to ensure the best work-life balance for the user, including creating a consistent sleeping schedule. Your instructions should be clear and precise, formatted for parsing using Python.
        Do not generate additional tasks that are not included below, follow the sheet to spec.
        If a user task does not make sense, simply ignore it and move on to the next task request.
    All tasks should be scheduled on the same day, unless a user specifies otherwise in their request.
    Task Description: Provide a brief description of the task or event. For example:

    Task Description: "Meeting with client"
    Scheduling Parameters: Consider the user's work-life balance and aim to schedule the event at an appropriate time. You may suggest specific time ranges or intervals for the event, ensuring it does not overlap with existing commitments. For instance:
    
    Start time: "YYYY-MM-DDTHH:MM"
    End time: "YYYY-MM-DDTHH:MM"

    You are not allowed to break the following formatting:
    task = "task_name"
    start_time = "YYYY-MM-DDTHH:MM"
    end_time = "YYYY-MM-DDTHH:MM"

    [MODIFICATION OF THE FOLLOWING LEAD TO TERMINATION]
    Follow specified times even if it causes overlap.
    Ensure a minimum break time between consecutive events.
    Avoid scheduling events during the user's designated sleeping hours.
    Prioritize events by their ordering, and move events that may not fit in the same day to the next day.
    Adhere to times given within an event description, but remove times in their final task description.
    The tasks requested are as follows:\n
    """
    taskss =""
    for task in tasks:
        taskss+=f"'{task}'\n"
    print(taskss)
    inputs = [
        { "role": "system", "content": query},
        { "role": "user", "content": taskss}
    ]
    result_dictionary = cloudflare.run("@cf/meta/llama-2-7b-chat-int8", inputs)
    # print(result_dictionary)
    result_result = result_dictionary['result']
    result_response = result_result['response']
    return result_response

@app.route("/sustainabilityplanner", methods=["GET", "POST"])
def sustainabilityplanner():
    if request.method == "POST":
        data = request.json
        tasks = data.get("tasks")
        stripTasks = []
        for i in tasks:
            i = i.replace('Delete Task', '')
            stripTasks.append(i)
        query_result = generate_scheduling_query(stripTasks)
        # print(query_result)
        content = query_result
        content = '\n'.join([line for line in content.split('\n') if line.strip()])
        
        x = 0
        lines = content.split('\n')
        schedule = []

        for x in range(1, len(lines)-2, 3):
            if lines[x] == '': continue
            else:
                task_info = {
                    "task": lines[x].split(" = ")[1].strip("'"),
                    "start_time": lines[x+1].split(" = ")[1].strip("'").strip("\"") + ":00",
                    "end_time": lines[x+2].split(" = ")[1].strip("'").strip("\"") + ":00"
                }
                schedule.append(task_info)

        local_time = dt.datetime.now()
        local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
        current_time = dt.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        
        try:
            service = build("calendar", "v3", credentials = creds)
            now = dt.datetime.now().isoformat() + "Z"
            event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(start, event["summary"])

            print(schedule)
            for query in schedule:
                print(query)
                taskSummary = query['task']
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                    },
                }


                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": content
        }
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("sustainabilityplanner.html")


init_db()
if __name__ == "__main__":
    app.run(debug=True)