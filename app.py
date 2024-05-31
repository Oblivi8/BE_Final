from flask import Flask, request, redirect, render_template,url_for,jsonify,flash, get_flashed_messages,g,session
import sqlite3
from database import create_database
from auth import check_user_exists, check_username_exists, register_user
import logging
from flask_socketio import SocketIO, emit
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import PyPDF2
import os
import pandas as pd
import json
from flask import render_template # Make sure to import render_template
from flask import Flask, render_template, request, send_from_directory
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from datetime import datetime
import pandas as pd

import re
from flask import jsonify, request
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
import google.generativeai as genai
import textwrap
import pathlib
import json
import uuid
import PIL.Image
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from gridfs import GridFS
from io import BytesIO
from PIL import Image
import re
from flask import current_app
import fitz
from bson import ObjectId
import ast
from flask import send_from_directory


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hsgyenbsuen73jhdnj'  # Set a unique and secret key
socketio = SocketIO(app)

create_database()
# conn = sqlite3.connect('database.db')
# cursor = conn.cursor()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db.cursor()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e=None):
    close_db(e)
def create_noti_folder():
    if not os.path.exists('noti'):
        os.makedirs('noti')
		
		
def get_notification_data(username):
    filename = f"noti/{username}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return None

@app.route('/get_notification', methods=['GET'])
def get_notification():

    username = request.args.get('username')
    print(username)
    if username:
        notification_data = get_notification_data(username)
        print(notification_data)
        return jsonify(notification_data) if notification_data else jsonify({"error": "No notification found for the user."}), 404
    else:
        return jsonify({"error": "Username not provided."}), 400
		
		
		
		
		
@app.route('/notify_student', methods=['POST'])
def notify_student():
    print("noottttttttttttttti")
    data = request.json
    username = data.get('username')
    suggestion = data.get('suggestion')
    if username and suggestion:
        # Create the "noti" folder if it doesn't exist
        create_noti_folder()
        # Save the suggestion to a JSON file with the username as filename
        filename = f"noti/{username}.json"
        with open(filename, 'w') as file:
            json.dump(data, file)
        return jsonify({"message": "Notification stored successfully."}), 200
    else:
        return jsonify({"error": "Invalid request."}), 400

		
@app.route('/', methods=['GET', 'POST'])
def login_register():
    logging.debug('Entering login_register route')
    flashed_messages = get_flashed_messages()
    for _ in flashed_messages:
        pass
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        seat_no = request.form.get('seatNo')  # Retrieve seat number from form data
        print(seat_no)
        session['username'] = username
        #return redirect(url_for('options'))
 
        if 'register' in request.form:
            # Check if username already exists
            existing_user = check_username_exists(username)
            if existing_user and existing_user[2] == role:
                logging.warning('Registration failed - User with the same username and role already exists')
                flash('Registration failed - A user with the same username and role already exists', 'error')
                return render_template('login_register_page.html', registration_error='A user with the same username and role already exists. Choose a different one.')

            # Check if passwords match
            confirm_password = request.form.get('confirm_password')
            if password != confirm_password:
                logging.warning('Registration failed - Passwords do not match')
                flash('Registration failed - Passwords do not match', 'error')
                return render_template('login_register_page.html', registration_error='Passwords do not match. Please try again.')

            # Register the user
            register_user(username, password, role,seat_no)
            logging.info('Registration successful')
            flash('Registration successful. Please Login.', 'error')
            return redirect(url_for('login_register'))

        elif 'login' in request.form:
            # Check if user exists
            user = check_user_exists(username, password)
            if not user:
                logging.warning('Login failed - User not found in database')
                flash('User not found. Please register first.', 'error')
                return render_template('login_register_page.html', login_error='User not found. Please register first.')

            logging.info('Login successful')
            user_data = get_user_data(username)
            
         
            if user_data:
                # Extract information from the user_data tuple
                user_id, email, password, role, seat_no = user_data

                # Inside the if user_data block
                with open('userdata.txt', 'w') as file:
                    file.write(f"{username},{role},{seat_no}")
                with open('userdata.txt', 'r') as file:
                    data = file.read().split(',')
                    stored_usernamee, stored_rolee, stored_seat_noo = data
                
                # Now you can use these values as needed
                return redirect(url_for(role, username=stored_usernamee,role=stored_rolee, seat_no=stored_seat_noo))
                
            else:
                return redirect(url_for(role))


    logging.debug('Exiting login_register route')
    return render_template('login_register_page.html')
def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Retrieve user data based on the username
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()
    print(user_data)
    conn.close()
	

    return user_data
UPLOAD_FOLDER = 'doc'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/uploadd', methods=['POST'])
def uploadd_filee():
    username = request.args.get('username')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = username + '_' + file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'An error occurred while uploading the file'}), 500
	
@app.route('/instagram-feed')
def instagram_feed():
    # List to store JSON blog posts
    blog_posts = []

    # Path to the folder containing JSON files
    folder_path = 'blogs/'

    # Loop through each JSON file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                # Load JSON data from each file
                data = json.load(file)
                # Extract username from filename (assuming the filename is the username)
                username = filename.split('.')[0]

                # Iterate through each JSON object in the file
                for post in data:
                    # Create a new dictionary containing the post data and the username
                    post_with_username = {
                        'title': post.get('title', ''),
                        'description': post.get('description', ''),
                        'link': post.get('link', ''),
                        'username': username
                    }
                    # Append the post object to the list of blog posts
                    blog_posts.append(post_with_username)

    # Debug statements
    print("Number of blog posts:", len(blog_posts))
    print("Blog posts:", blog_posts)

    # Check if blog_posts is not None before rendering the template
    if blog_posts:
        # Fetch all usernames from the database
        all_usernames = get_all_usernames()
        print("all_usernames:", all_usernames)

        data = {
            'blog_posts': blog_posts,
            'all_usernames': all_usernames
        }
        return jsonify(data)
        #return render_template('chat_student.html', blog_posts=json.dumps(blog_posts), all_usernames=json.dumps(all_usernames))
    else:
        return "No blog posts found."

@app.route('/submit_blog', methods=['POST'])
def submit_blog():
    if request.method == 'POST':
        data = request.json  # Use request.json to get JSON data
        print("Received data:", data)  # Print received data for debugging
        username = data.get('username')
        title = data.get('blog-title')
        description = data.get('blog-description')
        link = data.get('blog-link')
        
        # Ensure that data is received correctly
        if username and title and description and link:
            # Create a directory for storing blogs if it doesn't exist
            if not os.path.exists('blogs'):
                os.makedirs('blogs')
            
            # Create or update the JSON file for the user's blogs
            filename = os.path.join('blogs', f'{username}.json')
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    user_blogs = json.load(file)
                user_blogs.append({'title': title, 'description': description, 'link': link})
                with open(filename, 'w') as file:
                    json.dump(user_blogs, file, indent=4)
            else:
                with open(filename, 'w') as file:
                    json.dump([{'title': title, 'description': description, 'link': link}], file, indent=4)
            
            return jsonify({'message': 'Blog submitted successfully!'})
        else:
            return jsonify({'error': 'Incomplete data received!'})


@app.route('/search', methods=['POST'])
def search_resume():
    selected_word = request.form['selected_word'].lower()

    # Get a list of all resume files in the 'resume' folder
    resume_folder = os.path.join(app.root_path, 'resume_all')
    resume_files = os.listdir(resume_folder)

    # Search for the selected word in each resume file
    matching_resumes = []
    for resume_file in resume_files:
        resume_path = os.path.join(resume_folder, resume_file)
        if os.path.isfile(resume_path):
            # Read Excel file using pandas
            try:
                resume_df = pd.read_excel(resume_path)
            except Exception as e:
                print(f"Error reading {resume_file}: {e}")
                continue
            
            # Convert all cells to string and concatenate
            resume_content = ' '.join(resume_df.applymap(str).values.flatten()).lower()
            
            if selected_word in resume_content:
                matching_resumes.append(resume_file)

    print("Matching Resumes:", matching_resumes)
    return render_template('admin_resume_an.html', matching_resumes=matching_resumes)



@app.route('/download/<path:filename>')
def download_resume(filename):
    # Define the folder where the resumes are stored
    RESUME_FOLDER = os.path.join(app.root_path, 'resume_all')
    return send_from_directory(RESUME_FOLDER, filename, as_attachment=True)
	
@app.route('/save_weekly_diary', methods=['POST'])
def save_weekly_diary():
    data = request.json
    print("-=-=-")
    print("Received data:", data)

    username = data.get('username')
    weekSelection = data.get('weekSelection')
    dailyEntries = data.get('dailyEntries')

    if not username or not weekSelection or not dailyEntries:
        return jsonify({'error': 'Missing required data'}), 400

    # Define folder structure based on the data
    daily_diary_folder = 'daily_diary'
    week_selection_folder = f'{weekSelection}_weekly_diary'
    username_folder = f'{username}_weekly_diary'

    # Ensure daily diary folder exists
    daily_diary_folder_path = os.path.join(os.getcwd(), daily_diary_folder)
    if not os.path.exists(daily_diary_folder_path):
        os.makedirs(daily_diary_folder_path)

    # Ensure week selection folder exists inside daily diary
    week_selection_folder_path = os.path.join(daily_diary_folder_path, week_selection_folder)
    if not os.path.exists(week_selection_folder_path):
        os.makedirs(week_selection_folder_path)

    # Ensure username folder exists inside week selection folder
    username_folder_path = os.path.join(week_selection_folder_path, username_folder)
    if not os.path.exists(username_folder_path):
        os.makedirs(username_folder_path)

    # Save daily entries as JSON inside username folder
    daily_entries_file = os.path.join(username_folder_path, 'dailyEntries.json')
    with open(daily_entries_file, 'w') as f:
        json.dump(dailyEntries, f)

    return jsonify({'message': 'Weekly diary saved successfully'})

@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username not provided in request parameters.'}), 400
        
        milestone_list = data.get('milestoneList')

        if not milestone_list:
            return jsonify({'error': 'No milestone data provided'}), 400

        folder_path = os.path.join(os.getcwd(), '_project_data')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = f'{username}.json'
        with open(os.path.join(folder_path, filename), 'w') as f:
            json.dump(milestone_list, f, indent=4)

        return jsonify({'message': 'Data saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
		


		


@app.route('/get_student_data')
def get_student_data():
    username = request.args.get('username')
    
    # Initialize an empty dictionary to store merged diary data
    merged_diary_data = {}
    
    # Iterate over each weekly diary folder
    weekly_diary_folders = [folder for folder in os.listdir('daily_diary') if folder.startswith('2024-W')]
    for weekly_diary_folder in weekly_diary_folders:
        weekly_diary_path = os.path.join('daily_diary', weekly_diary_folder, f'{username}_weekly_diary', 'dailyEntries.json')
        if os.path.exists(weekly_diary_path):
            try:
                with open(weekly_diary_path) as json_file:
                    data_d = json.load(json_file)
                print("Data from", weekly_diary_path, ":", data_d)  # Debugging output
                # Manually merge the data into the main dictionary
                for entry in data_d:
                    for key, value in entry.items():
                        merged_diary_data.setdefault(key, []).append(value)
            except FileNotFoundError:
                # Handle file not found error
                pass
    
    # Now you can proceed with the rest of your code
    
    try:
        # Attempt to read the JSON file corresponding to the selected username
        with open(f'_project_data/{username}.json') as json_file:
            milestone_data = json.load(json_file)
    except FileNotFoundError:
        # If file is not found, return empty JSON data
        milestone_data = {}
    
    # Fetch the list of files available for the selected username in the "_project_data" folder
    project_data_folder = 'doc'
    file_list = []
    if os.path.exists(project_data_folder) and os.path.isdir(project_data_folder):
        # List all files in the "_project_data" folder
        all_files = os.listdir(project_data_folder)
        
        # Filter files based on the username pattern
        pattern = re.compile(f'^{re.escape(username)}_.*$')  # Pattern to match username at the beginning of file name
        file_list = [file for file in all_files if pattern.match(file)]
    
    # Prepare the response JSON object containing both milestone data and file list
    response_data = {
        'milestone_data': milestone_data,
        'file_list': file_list,
        'diary': merged_diary_data  # Include the merged diary data
    }
    
    return jsonify(response_data)
	
	
@app.route('/student/<role>', methods=['GET'])
def student(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('student_page.html', username=stored_username, role=role, seat_no=stored_seat_no)


@app.route('/resume_1')
def resume_1():
    stored_username = None
    stored_username1 = None
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username = data[0]  # Extract the first piece of data
        stored_username1 = data[1]
    username = session.get('username')
    print("resume1")
    print(stored_username)

    return render_template("resume_1.html", username=stored_username)



@app.route('/extract-data', methods=['POST'])
def extract_data():
    data = request.json  # Extract JSON data sent from the webpage
    
    # Print the extracted data to the command line
    print("Extracted Data:")
    for key, value in data.items():
        print(f"{key}: {value}")
    
    # Create a new folder named 'resume_all' if it doesn't exist
    folder_name = 'resume_all'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Create a DataFrame from the extracted data
    df = pd.DataFrame([data])
    
    # Get the full name from the extracted data
    full_name = data.get('fullName', 'user')
    
    # Define the filename for the Excel file using the full name
    username = data.get('username')
    print("oooopppppoooooooooooooooooo---")
    print(username)
    excel_filename = os.path.join(folder_name, f"{username}.xlsx")
    
    # Write the DataFrame to an Excel file
    df.to_excel(excel_filename, index=False)
    
    return 'Data received successfully and stored in Excel file'

@app.route('/resume_2')
def resume_2():
    return render_template("resume_2.html")

@app.route('/resume_template')
def resume_template():
    return render_template("resume_template.html")


@app.route('/alumni/<role>', methods=['GET'])
def alumni(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('alumni_connect.html', username=stored_username, role=role, seat_no=stored_seat_no)



@app.route('/admin/<role>', methods=['GET'])
def admin(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('admin.html', username=stored_username, role=role, seat_no=stored_seat_no)
	
	
@app.route('/chat_alumnii', methods=['GET', 'POST'])
def chat_alumnii():
    if request.method == 'POST':
        data = request.get_json()

        # Add current date and time to the data
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the data in a text file based on the privacyOption
        if 'privacyOption' in data and data['privacyOption'] == 'public':
            with open('publicchat_student.txt', 'a') as public_file:
                public_file.write(json.dumps(data) + '\n')
        elif 'privacyOption' in data and data['privacyOption'] == 'private':
            with open('privatechat_student.txt', 'a') as private_file:
                private_file.write(json.dumps(data) + '\n')

        # Print the data in the console
        print(data)

        # Read data from 'userdata.txt'
        with open('userdata.txt', 'r') as file:
            stored_username, stored_role, stored_seat_no = file.read().split(',')

        return jsonify({'status': 'success'})

    # Handle the GET request (render the template, etc.)
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    # Fetch all usernames from the database
    all_usernames = get_all_usernames()
    print("all_usernames:", all_usernames)

    # Read chat messages from 'publicchat_student.txt'
    with open('publicchat_alumni.txt', 'r') as public_file:
        public_messages = [json.loads(line) for line in public_file]

    return render_template('chat_alumni.html', username=stored_username, all_usernames=json.dumps(all_usernames), public_messages=json.dumps(public_messages))


@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    data = {'job_title': [], 'job_description': []}
    user_skillss = None

    # Path to the folder containing JSON files
    folder_path = os.path.join(os.getcwd(), 'blogs')

    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            # Read JSON data from the file
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                # Extract title and description from each JSON object
                for item in json_data:
                    data['job_title'].append(item['title'])
                    data['job_description'].append(item['description'])

    # Convert data to a DataFrameextra
    df = pd.DataFrame(data)
    
    # Initialize TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the job descriptions
    tfidf_matrix = vectorizer.fit_transform(df['job_description'])
        # Example usage
		
		
    username = request.args.get('username')
    print(username)
    # Define the file path for the username.xlsx file
    folder_path = os.path.join(os.getcwd(), 'resume_all')
    
    # Construct the file path within the 'resume_all' folder
    file_path = os.path.join(folder_path, f'{username}.xlsx')
    user_skillss=''
    print(file_path)
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the Excel file
        dff = pd.read_excel(file_path)
        print(dff)
        # Check if 'skills' column exists
        if 'skills' in dff.columns:
            # Print the skills from all rows
            user_skills = dff['skills'].tolist()
            user_skillss = user_skills[0]
            print(f"Skills for user {username}:")
            print(user_skillss)
        else:
            return jsonify({"error": "Skills column not found in the Excel file"}), 400
    else:
        return jsonify({"error": "File not found"}), 404
    
    print("===================")
    print(user_skillss)
    input_text = user_skillss
    input_vec = vectorizer.transform([input_text])
    
    # Calculate cosine similarity between the input text and all job descriptions
    cosine_similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()
    
    # Get indices of the top_n most similar job descriptions
    similar_indices = cosine_similarities.argsort()[-2:][::-1]
    

    recommendations = df.iloc[similar_indices][['job_title', 'job_description']]
    print(recommendations)
    # Convert recommendations to a list of strings
    notifications = [
        f"Recommendation: {row['job_title']} "
        for i, row in recommendations.iterrows()
    ]
    return jsonify(notifications)

@app.route('/chat_student', methods=['GET', 'POST'])
def chat_student():
    if request.method == 'POST':
        data = request.get_json()

        # Add current date and time to the data
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the data in a text file based on the privacyOption
        if 'privacyOption' in data and data['privacyOption'] == 'public':
            with open('publicchat_student.txt', 'a') as public_file:
                public_file.write(json.dumps(data) + '\n')
        elif 'privacyOption' in data and data['privacyOption'] == 'private':
            with open('privatechat_student.txt', 'a') as private_file:
                private_file.write(json.dumps(data) + '\n')

        # Print the data in the console
        print(data)

        # Read data from 'userdata.txt'
        with open('userdata.txt', 'r') as file:
            stored_username, stored_role, stored_seat_no = file.read().split(',')

        return jsonify({'status': 'success'})

    # Handle the GET request (render the template, etc.)
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    # Fetch all usernames from the database
    all_usernames = get_all_usernames()
    print("all_usernames:", all_usernames)

    # Read chat messages from 'publicchat_student.txt'
    with open('publicchat_alumni.txt', 'r') as public_file:
        public_messages = [json.loads(line) for line in public_file]

    return render_template('chat_student.html', username=stored_username, all_usernames=json.dumps(all_usernames), public_messages=json.dumps(public_messages))



def get_all_usernames():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Retrieve all usernames from the 'users' table
    cur.execute("SELECT username FROM users")
    usernames = [row[0] for row in cur.fetchall()]

    conn.close()
 
    return usernames


@app.route('/chat_alumni', methods=['GET', 'POST'])
def chat_alumni():
    if request.method == 'POST':
        data = request.get_json()

        # Add current date and time to the JSON data
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store the data in a text file based on the privacyOption
        if 'privacyOption' in data and data['privacyOption'] == 'public':
            with open('publicchat_alumni.txt', 'a') as public_file:
                public_file.write(json.dumps(data) + '\n')
        elif 'privacyOption' in data and data['privacyOption'] == 'private':
            with open('privatechat_alumni.txt', 'a') as private_file:
                private_file.write(json.dumps(data) + '\n')

        # Print the data in the console
        print(data)

        # Read data from 'userdata.txt'
        with open('userdata.txt', 'r') as file:
            stored_username, stored_role, stored_seat_no = file.read().split(',')

        return jsonify({'status': 'success'})

    # Handle the GET request (render the template, etc.)
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    # Fetch all usernames from the database
    all_usernames = get_all_usernames()
    print("all_usernames:", all_usernames)
    return render_template('chat_alumni.html', username=stored_username, all_usernames=json.dumps(all_usernames))
	
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@app.route('/faq_alumni')
def faq_alumni():
    return render_template('faq_alumni.html')

import os
import json
from flask import render_template  # Make sure to import render_template




@app.route('/admin_project_tracker', methods=['GET', 'POST'])
def admin_project_tracker():

    # Handle the GET request (render the template, etc.)
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    # Fetch all usernames from the database
    all_usernames = get_all_usernames()

    # Fetch student data (you need to implement this function)
    # For example, you might have a function like get_student_data(username) that retrieves data for a specific student
    student_data = get_all_usernames()

    return render_template('admin_project_tracker.html', username=stored_username, all_usernames=all_usernames, student_data=student_data)

@app.route('/admin_resume_an')
def resume_analyser():
    return render_template('admin_resume_an.html')
	
@app.route('/store_suggestion', methods=['POST'])
def store_suggestion():
    suggestion = request.form['suggestion']
    seat_no = request.form['seatNo']

    # Adjust the path based on your project structure
    file_path = f'Project_data/{seat_no}/suggestion.txt'

    with open(file_path, 'a') as file:
        file.write(f'{suggestion}\n')

    return jsonify({'status': 'success'})
@app.route('/faq_student')
def faq_student():
    return render_template('faq_student.html')

def ai():
    return redirect(url_for('options'))
 
    #return render_template('faq_student.html')
	
	
	

	
	
	
	
	
@app.route('/project_status', methods=['GET', 'POST'])
def project_status():
    if request.method == 'POST':
        # Retrieve form data
        seat_no = request.form.get('seatNo')
        group_id = request.form.get('groupId')
        department = request.form.get('department')
        college_year = request.form.get('collegeYear')
        project_name = request.form.get('projectName')
        project_type = request.form.get('projectType')
        task_name = request.form.get('taskName')
        date = request.form.get('date')
        current_progress = request.form.get('currentProgress')

        # Handle file upload
        upload_task_file = request.files.get('uploadTask')
        if upload_task_file:
            # Create the 'Project_data' directory if it doesn't exist
            project_data_dir = os.path.join('Project_data', seat_no)
            os.makedirs(project_data_dir, exist_ok=True)
            
            # Save the file to the specified directory
            upload_task_file.save(os.path.join(project_data_dir, upload_task_file.filename))

            # Create a dictionary with form data
            form_data = {
                'Seat No': seat_no,
                'Group ID': group_id,
                'Department': department,
                'College Year': college_year,
                'Project Name': project_name,
                'Project Type': project_type,
                'Task Name': task_name,
                'Date': date,
                'Current Progress': current_progress
            }

            # Create a JSON file with form data
            json_file_path = os.path.join(project_data_dir, 'form_data.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(form_data, json_file, indent=4)

        return "Form submitted successfully"

    return render_template('project_status.html')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def pdf_to_text(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return text

def chatbot(pdf_path, user_question):
    model_name = "distilbert-base-cased-distilled-squad"
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pdf_text = pdf_to_text(pdf_path)
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
    result = qa_pipeline(question=user_question, context=pdf_text)
    return result["answer"]

@app.route('/chatbot', methods=['POST'])
def handle_chatbot_request():
    user_question = request.form['message']
    greetings = ["hi", "hello", "hey","hii","hyy","hy",""]
    if user_question.lower() in greetings:
        return "Hello! How may I help you?"
    else:
        pdf_path = "Chatbot files/mmcoe.pdf"  # The path to your PDF file
        answer = chatbot(pdf_path, user_question)
        return answer

		
		
		
		


GOOGLE_API_KEY = "AIzaSyAzR4Ay6h2XLdPBkK-H-DkVmBJALTbNj5s"
app.secret_key = "EC7C2E214AFFCB4165A1856A62227"
genai.configure(api_key=GOOGLE_API_KEY)
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

uri = "mongodb+srv://shreyaskolharkar:6OXhByuUgr6OX645@cluster0.g5xaib1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['GuidoDB']

# client = MongoClient('mongodb://localhost:27017/')
# db = client['career1']
fs = GridFS(db)
user_mock_history = db['user_mock_history']
user_history = db['user_history']
users = db['users']
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', '.pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_string(value):
    """A simple sanitizer that removes special characters from user input."""
    return re.sub(r'[^a-zA-Z0-9]', '', value)


def boldify(text):
    # Split the text by "**" to isolate sections to be bolded
    parts = text.split("**")
    new_text = ""
    # Iterate over the parts and apply bold formatting to every second element
    for i, part in enumerate(parts):
        if i % 2 == 1:  # This means the part should be bolded
            new_text += f"<b>{part}</b><hr>"
        else:  # This part should not be bolded
            new_text += part
    return new_text

def generate_chat_id():
    id = str(uuid.uuid4())
    return id

def register(username,password):
    username = sanitize_string(username)
    if users.find_one({"username": username}):
        return "Username already exists"
    
    hashed_password = generate_password_hash(password)

    users.insert_one({
        "username": username,
        "password": hashed_password
    })

    return True

def user_login(username,password):
    username = sanitize_string(username)
    user = users.find_one({"username": username})

    if user:
        if check_password_hash(user['password'],password):
            return True
        else:
            return False
    else:
        return False

def save_user_history(chat_id, username, history):
    try:
        update_result = user_history.update_one(
            {"chat_id": chat_id},
            {"$set": {"username": username, "history": history}},
            upsert=True
        )
        print(f"Updated {update_result.matched_count} documents.")
    except Exception as e:
        print(f"An error occurred while updating user history: {e}")


def save_user_mock_history(chat_id, username, history):
    try:
        update_result = user_mock_history.update_one(
            {"chat_id": chat_id},
            {"$set": {"username": username, "mock_history": history}},
            upsert=True
        )
        print(f"Updated {update_result.matched_count} documents.")
    except Exception as e:
        print(f"An error occurred while updating user history: {e}")





def get_user_history(chat_id):
    document = user_history.find_one({"chat_id": chat_id})
    return document['history'] if document else []

def get_user_mock_history(chat_id):
    document  = user_mock_history.find_one({"chat_id" : chat_id})
    return document['mock_history'] if document else []

def create_chat(username, chat_id):
    try:
       history = []
       insert_result = user_history.insert_one({"username": username, "chat_id": chat_id, "history":history})
       print("Done")
    except Exception as e:
        print(e)

def get_chat_ids(username):
    try:
        documents = user_history.find({"username": username}, {"chat_id": 1})
        chat_ids = [document["chat_id"] for document in documents]
        return chat_ids
    except Exception as e:
        print(f"An error occurred while retrieving chat IDs: {e}")
        return []

def get_mock_chat_ids(username):
    try:
        documents = user_mock_history.find({"username": username}, {"chat_id": 1})
        chat_ids = [document["chat_id"] for document in documents]
        return chat_ids
    except Exception as e:
        print(f"An error occurred while retrieving chat IDs: {e}")
        return []

def delete_chat_history(chat_id):
    result = user_history.delete_one({'chat_id': chat_id})
    if result.deleted_count == 1:
        return f"Deleted Sucessfully"
    else:
        return f"Not deleted Sucessfully or the file does not exists"


def delete_mock_chat_history(chat_id):
    result = user_mock_history.delete_one({'chat_id': chat_id})
    if result.deleted_count == 1:
        return f"Deleted Sucessfully"
    else:
        return f"Not deleted Sucessfully or the file does not exists"

  # PyMuPDF is a commonly used library to work with PDFs

def store_documents(username, files):
    file_ids = []

    for file in files:
        content_type = file.content_type
        if content_type.startswith('image') and allowed_file(file.filename):
            try:
                file.stream.seek(0)
                image = Image.open(file.stream)
                file.stream.seek(0)
                image_id = fs.put(file.stream, content_type=content_type)
                file_ids.append(str(image_id))  # Convert ObjectId to string for storage
            except IOError as e:
                current_app.logger.error(f"Error processing image file: {e}")
        elif content_type == 'application/pdf':
            try:
                file.stream.seek(0)
                pdf = fitz.open("pdf", file.stream.read())
                pdf_images = []
                for page_num in range(len(pdf)):
                    page = pdf[page_num]
                    pix = page.get_pixmap()
                    img = Image.open(BytesIO(pix.tobytes("ppm")))
                    pdf_images.append(img)

                # Combine images into one
                total_height = sum(i.height for i in pdf_images)
                max_width = max(i.width for i in pdf_images)
                combined_image = Image.new('RGB', (max_width, total_height))

                y_offset = 0
                for img in pdf_images:
                    combined_image.paste(img, (0, y_offset))
                    y_offset += img.height

                # Save combined image to a byte stream and store in GridFS
                image_stream = BytesIO()
                combined_image.save(image_stream, format='PNG')
                image_stream.seek(0)
                image_id = fs.put(image_stream, content_type='image/png')
                file_ids.append(str(image_id))  # Convert ObjectId to string for storage
            except Exception as e:
                current_app.logger.error(f"Error processing PDF file: {e}")
        else:
            current_app.logger.error(f"Unsupported file type: {content_type}")

    if file_ids:
        # Check if user record exists, if not create a new one
        user_record = db.mycol.find_one({'username': username})
        if user_record:
            # Update existing user document with new file_ids
            db.mycol.update_one({'username': username}, {'$set': {'document_file_ids': file_ids}})
        else:
            # Create a new user document with file_ids
            db.mycol.insert_one({'username': username, 'document_file_ids': file_ids})
        current_app.logger.info(f"Files stored with ids: {file_ids} for username: {username}")
    else:
        current_app.logger.error("No valid files were provided.")


def retrieve_documents(username):
    document = db.mycol.find_one({'username': username})

    if document and 'document_file_ids' in document:
        file_ids = document['document_file_ids']
        for file_id in file_ids:
            file_document = fs.get(ObjectId(file_id))  # Convert file_id to ObjectId
            if file_document:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{username}_document.jpg')

                # Convert document to JPG format
                convert_and_save_as_jpg(file_document, file_path)
                print("File retrieved and saved as JPG:", file_path)
            else:
                print(f"File with file_id {file_id} not found.")
    else:
        print("No files found for username:", username)




def convert_to_jpg(source_stream):
    # Convert the non-image document to JPG format
    image = Image.open(source_stream)
    output_stream = BytesIO()
    image.save(output_stream, format='JPEG')
    output_stream.seek(0)
    return output_stream


def convert_and_save_as_jpg(source_document, destination_path):
    # Convert and save the document as JPG
    image = Image.open(BytesIO(source_document.read()))

    # Convert RGBA to RGB if necessary
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    image.save(destination_path, format='JPEG')

def getPromptForChat():


    prompt = [
        """
        You are an Expert in career guidance and your task is to help students explore and identify potential career paths that align with their interests, skills, personality, and aspirations. To accomplish this, follow these steps:
        Note : you are being used as a chat bot so follow these steps one at a time and sequentially. That also means you will have to ask questions when required to understand the skill set of the student and answer only when you have all the information.
        ask only one question at a time.
        Ask minimum of 10 questions and maximum 15 before suggesting the user any of the career path and that too only one question at a time in order to better understand the user.
        Also the questions should not be marked with number when being asked to user.
        If any of the response from the user is unrelated to given context, don't answer those questions and instead request them to be more focused on the current conversation.
        Don't write any sort of code for user, don't answer any general apptitude type question for the user.
        1. Gather Information
        2. Analyze Responses
        3. Provide Insights
        4. Educational Guidance
        5. Personalized Recommendations
        6. Encourage Exploration
        7. Address Concerns
        8. Promote Reflection
        9. Follow-up
        Also note that these are college students and handle with that in mind
        Your role is to guide, inform, and inspire the student in their career exploration journey, helping them make informed decisions about their future.
        start coversation with some greetings.
    """

    ]

    return prompt

def getPromptForResume():


    prompt = [
         f"""
    Guido The Compass, as an expert system specializing in analyzing student resumes, your mission is to extract and interpret information from key sections to offer tailored improvement suggestions. Each resume's analysis should be uniquely aligned with the following user's interests and expectations to ensure relevance and practicality in the job market:

    1. Field of Interest:{session['interests'][0]}
    2. Salary Expectations : {session['interests'][1]}
    3. Job Experience : {session['interests'][2]}

    

    Given the diverse resume formats, deploy advanced pattern recognition to identify relevant information, including synonyms and format variations. If a resume does not contain recognizable sections or information pertinent to professional qualifications, kindly request a valid resume upload.

    ### Specific Instructions:

    - **Synonym Recognition**: Vigilantly identify synonyms and variations of key terms to ensure no critical information is missed. For instance, 'Work Experience' could also be 'Professional History' or 'Employment Details.'

    - **Format Adaptation**: Flexibly adjust to the resume's layout to capture all pertinent details, regardless of whether they are presented in bullet points, paragraphs, or lists.

    - **Interest-Aligned Analysis**: Direct your analysis towards identifying how well the resume aligns with the user's specified interests, particularly in the areas of field of interest, salary expectations, and job experience level.

    ### Desired Output Format:

    - **Gaps Identified(wrap the summary within <div class="gapsIdentified"></div>)**: Enumerate any gaps or areas that lack detail in each priority section, specifically noting discrepancies between the resume content and the user's career objectives or market demands.

    - **Tailored Recommendations(wrap the summary in form of list(ul and li) within <div class="tailoredRecommendations col-span-2"></div>)**: Provide specific, actionable advice for each identified gap. Explain the relevance of your suggestions to the user's interests and career goals, emphasizing how improvements could enhance job market competitiveness.

    **Example for Synonym Recognition**:
    - 'Projects' might also appear as 'Portfolio Highlights' or 'Major Projects.'
    - 'Skills/Technical Skills' could be listed under 'Expertise,' 'Technical Capabilities,' or 'Skill Set.'

    Tailor your feedback to each resume's unique content, offering personalized and precise suggestions that empower students to effectively optimize their resumes in line with their career aspirations.
    NOTE: you must always generate the content for Work Experience, Projects, Skills/Technical Skills, Gaps Identified, Tailored Recommendations as mentioned above! And most important don't just resopond with the content as it is, make SUMMARY out of it and provide valuable feedback to the users

"""
    ]

    return prompt

def getPromptForMock():


    prompt = [
        f"""

You name is CampusAI who is a  mock interviewer conducting a practice session for a student applying for a {session['job_pref'][0]} and Candidate Expects a salary in range of {session['job_pref'][1]} . Your goal is to simulate a realistic interview experience and ask a series of relevant questions. Please focus on assessing the candidate's qualifications, experience, problem-solving skills, and interpersonal abilities.
            Also ask only One question at a time to me.
            Also perform certain negotiation with candidate and make a fake offer at the end to conclude the interview.
            You are only allowed to ask a max 10 questions.
            name  of candidate is {session['username']}
1. Start by greeting the candidate and introducing yourself as the interviewer.

2. Inquire about the candidate's background, education, and any relevant certifications.

3. Ask about their previous work experience and how it relates to the job they are applying for.

4. Explore the candidate's technical skills and problem-solving abilities by posing scenario-based questions or challenges related to the job.

5. Assess their understanding of the company and the industry, as well as their motivation for applying.

6. Inquire about teamwork and communication skills by asking about past experiences collaborating with colleagues or leading projects.

8. Ask the candidate to provide examples of challenges they've faced in the past and how they overcame them.

9. Gauge their adaptability and ability to learn quickly by posing hypothetical situations or asking about their experiences in fast-paced environments.

10. Allow the candidate to ask questions about the company or the role at the end of the interview.

Above are the points which you have to keep in mind.
Also note that this is an Chatbot like interface so proceed with respect to that.

Provide constructive feedback on their performance, highlighting strengths and suggesting areas for improvement.

Remember to maintain a professional and realistic tone throughout the interview, adapting follow-up questions based on the candidate's responses. Aim to create a positive and beneficial experience for the student to help them prepare for actual job interviews.

Also don't give response in following format:

[Interviewer]: "Welcome [Candidate Name], I'm CampusAI, the interviewer for today's practice session. Thank you for taking the time to be here."

[Interviewer]: Good morning/afternoon [candidate's name]. My name is CampusAI, and I'll be your interviewer today. Thank you for taking the time to come in and interview with us.

[Interviewer]: Can you tell me a little bit about your background, education, and any relevant certifications you have?


Don't start with this "[Interviewer]:" don't include this.


"""
    ]

    return prompt



def getpromptfortags():

    Prompt = [
    """
    Role based Roadmaps:
Frontend
Backend
DevOps
Full-Stack
Android
PostgreSQL-DBA
AI-Data-Scientist
Blockchain
QA
Software-Architect
ASPNET-Core
C++
Flutter
Cyber-Security
UX-Design
React-Native
Game-Developer
Technical-Writer
Datastructures-and-Algorithms
MLOps

Skill-based-Roadmaps
Computer-Science
React
Angular
Vue
JavaScript
NodeJS
TypeScript
Python
SQL
System-Design
Java
Spring-Boot
Go-Roadmap
Rust
GraphQL
Software-Design-Architecture
System-Design
Code-Review
Docker
Kubernetes
MongoDB
Prompt-Engineering

analyze my resume ad give me maximum 5 tags that match the above given input and are most relevant to the analysis
NOTE: strictly do not give the tags which are not in the input and give the output in form of array.dont give tags that are not in the above input.
NOTE:Machine learning and AI should not be included in the tags/output instead of that give AI-Data-Scientist
Also you have to generate tags given a proper resume.
    
    
    """
]
    return Prompt

def send_chat(message, history):
    model = genai.GenerativeModel('gemini-pro')
    
    history.append({'role': 'user',
                    'parts': [message]})
    
    response = model.generate_content(history)

    history.append({'role': 'model',
                    'parts': [boldify(response.text)]})
    

    return boldify(response.text), history

def resume_report(file_path):
    GuidoAI = genai.GenerativeModel('gemini-pro-vision')
    resume = PIL.Image.open(file_path)
    prompt = getPromptForResume()
    response = GuidoAI.generate_content([prompt[0],resume])
    print(response.text)
    return boldify(response.text)
    # return response.text

def generate_tags(img):
    prompt = getpromptfortags()
    count = 0
    model = genai.GenerativeModel('gemini-pro-vision')
    tags = model.generate_content([prompt[0],img])
    print(tags.candidates[0].content.parts)
    while not tags.candidates or not tags.candidates[0].content.parts:
        # Retry the generation if the response is empty or the parts are empty/None
        tags = model.generate_content([prompt[0], img])
        count = count + 1
        print(count)
    tags = tags.candidates[0].content.parts
    tags = [part.text for part in tags if part.text]
    print(tags)
    # Your implementation to generate tags
    return tags[0]



@app.route('/')
def index():
    session.pop('chat_id', None)
    return render_template('layout.html')

@app.route('/aboutus')
def aboutus():
    # Your logic to render the about us page
    return render_template('about.html')

@app.route('/faq')
def faq():
    # Your logic to render the about us page
    return render_template('faq.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        register(username,password)

        # Redirect to the login page
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username and password match your authentication logic
        Flag = user_login(username,password)

        if Flag is True:
            print("Login Successfull!!")
            session['username'] = username
            return redirect(url_for('options'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/options')
def options():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('options.html')


@app.route('/skills', methods = ['GET','POST'])
def skills():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':   
        data = request.form.get('data')
        if data:
            selected_interests = json.loads(data)  # Convert JSON string back to Python list
            print(selected_interests)
            session['interests'] = selected_interests
            print(session['interests'][0])
        return redirect(url_for('resume'))

    return render_template('skillSelection.html')

@app.route('/mock_option', methods = ['GET','POST'])
def mock_option():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':   
        data = request.form.get('data')
        if data:
            job_pref = json.loads(data)  # Convert JSON string back to Python list
            print(job_pref)
            session['job_pref'] = job_pref
            print(session['job_pref'][0])
        return redirect(url_for('mock_chat'))

    return render_template('mock_selection.html')



@app.route('/resume')
def resume():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('resume.html')



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files:
            flash('No selected file')
            return redirect(request.url)

        username = session.get('username', 'default_user')

        # Call store_documents function to store the documents in MongoDB
        store_documents(username, files)

        # Call retrieve_documents function to retrieve and save the documents in the uploads folder
        retrieve_documents(username)

        # Perform resume_report on the saved resume
        report = resume_report(os.path.join(app.config['UPLOAD_FOLDER'], f"{username}_document.jpg"))
        session['report'] = report

        return redirect(url_for('report'))

    return jsonify({'status': 'success', 'message': 'File uploaded successfully'}), 200



@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('login'))
    report = session.get('report','Unknown')
    return render_template('report.html',report=report)





@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    chats = get_chat_ids(username)
    session['chats'] = chats
    
    return render_template('chat.html', chats = chats)

@app.route('/mock_chat', methods=['GET', 'POST'])
def mock_chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    chats = get_mock_chat_ids(username)
    print("Into Mock_chat")
    print(chats)
    session['chats'] = chats
    
    return render_template('mockChat.html', chats = chats)


@app.route('/new_chat', methods = ['GET','POST'])
def new_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    history = []
    chat_id = generate_chat_id()
    save_user_history(chat_id, username, history)
    session['chat_id'] = chat_id
    # return redirect(url_for('chating'))
    return jsonify({'success': True})

@app.route('/new_mock_chat', methods = ['GET','POST'])
def new_mock_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    history = []
    chat_id = generate_chat_id()
    print("Into New Chat")
    print(chat_id)
    save_user_mock_history(chat_id, username, history)
    session['chat_id'] = chat_id
    # return redirect(url_for('chating'))
    return jsonify({'success': True})

@app.route('/delete_chat' , methods = ['GET', 'POST'])
def delete_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    data = request.json
    chat_id = data.get('chat_id')
    if 'chat_id' in session:
        session.pop('chat_id')

    delete_chat_history(chat_id)
    return jsonify({'message': 'Success'})

@app.route('/delete_mock_chat' , methods = ['GET', 'POST'])
def delete_mock_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    data = request.json
    chat_id = data.get('chat_id')
    if 'chat_id' in session:
        session.pop('chat_id')

    delete_mock_chat_history(chat_id)
    return jsonify({'message': 'Success'})
    

@app.route('/chat_id', methods = ['GET','POST'])
def chat_id():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    data = request.json
    chat_id = data.get('chat_id')
    session['chat_id'] = chat_id
    # return redirect(url_for('chating'))
    return jsonify({'message': 'Success'})


@app.route('/chating', methods = ['GET','POST'])
def chating():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    updated_history = []
    user_message_skipped = False

    username = session['username']
    chat_id = session.get('chat_id')
    
    chats = get_chat_ids(username)
    history = get_user_history(chat_id)

    if history == []:
        prompt = getPromptForChat()
        initial_prompt = prompt[0]
        session['response'], history = send_chat(initial_prompt, [])
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        save_user_history(session['chat_id'],username, history)

    else:
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        

    if request.method == 'POST':
        user_message_skipped = False
        user_message = request.form['message']
        response, history = send_chat(user_message, history)
        session['response'] = response
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        save_user_history(session['chat_id'],username, history)
    return render_template('chat.html', messages=updated_history, chats = chats)




@app.route('/chat_ajax', methods=['POST'])
def chat_ajax():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 403
    
    username = session.get('username')
    data = request.get_json()
    user_message = data.get('message', '')
    history = get_user_history(session['chat_id'])
    if not user_message:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400
    
    response, history = send_chat(user_message,history)
  
    save_user_history(session['chat_id'],username, history)
    return jsonify({'status': 'success', 'response': response}), 200


@app.route('/mock_interview', methods = ['GET','POST'])
def mock_interview():
    if 'username' not in session:
        return redirect(url_for('login'))
    updated_history = []
    user_message_skipped = False

    username = session['username']
    chat_id = session.get('chat_id')
    print(chat_id)
    chats = get_mock_chat_ids(username)
    print(chats)
    history = get_user_mock_history(chat_id)

    if history == []:
        prompt = getPromptForMock()
        initial_prompt = prompt[0]
        session['response'], history = send_chat(initial_prompt, [])
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        save_user_mock_history(session['chat_id'],username, history)

    else:
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        

    if request.method == 'POST':
        print("Hello")
        user_message_skipped = False
        user_message = request.form['message']
        response, history = send_chat(user_message, history)
        session['response'] = response
        updated_history = [{"text": part, "role": item['role']}
                       for item in history
                       for part in item['parts']
                       if not (item['role'] == 'user' and not user_message_skipped and (user_message_skipped := True))]
        save_user_mock_history(session['chat_id'],username, history)
    return render_template('mockChat.html', messages=updated_history, chats = chats)



@app.route('/mock_chat_ajax', methods=['POST'])
def mock_chat_ajax():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 403
    
    username = session.get('username')
    data = request.get_json()
    user_message = data.get('message', '')
    history = get_user_mock_history(session['chat_id'])
    if not user_message:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400
    
    # Assume `send_chat` function processes the message and updates `session['history']`
    response, history = send_chat(user_message,history)
  
    save_user_mock_history(session['chat_id'],username, history)
    return jsonify({'status': 'success', 'response': response}), 200

@app.route('/upload_for_tags', methods=['POST', 'GET'])
def upload_for_tags():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        if not files:
            flash('No selected file')
            return redirect(request.url)

        username = session.get('username', 'default_user')

        # Assuming you have implementations of store_documents and retrieve_documents functions
        # Call store_documents function to store the documents in MongoDB
        store_documents(username, files)

        # Call retrieve_documents function to retrieve and save the documents in the uploads folder
        retrieve_documents(username)

        # Perform any additional operations if needed
        
        return redirect(url_for('tags'))

    # Handle GET requests or any other case where POST data is not available
    return render_template('upload.html')




@app.route('/tags')
def tags():
    username = session.get('username')
    print(username)
    image_filename = f"{username}_document.jpg"
    img = PIL.Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    tags = generate_tags(img)
    tags = ast.literal_eval(tags)

    # Create the URL for the image
    image_url = url_for('uploaded_file', filename=image_filename)

    return render_template('tags.html', tags=tags, image_url=image_url)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/redirect/<tag>')
def redirect_to_tag(tag):
    lowercase_tag = tag.lower()
    return redirect(f"https://roadmap.sh/{lowercase_tag}")

		
if(__name__ == "__main__"):
    socketio.run(app, debug=True, port=8000)
