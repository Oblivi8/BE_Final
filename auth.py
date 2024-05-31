

import sqlite3
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

def check_user_exists(username, password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user

def check_username_exists(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user

def register_user(username, password, role, seat_no):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Check if the 'seat_no' column exists in the 'users' table
    cur.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cur.fetchall()]

    if 'seat_no' not in columns:
        # 'seat_no' column doesn't exist, so add it
        cur.execute("ALTER TABLE users ADD COLUMN seat_no TEXT")

    # Insert data into the 'users' table
    cur.execute("INSERT INTO users (username, password, role, seat_no) VALUES (?, ?, ?, ?)", (username, password, role, seat_no))

    conn.commit()
    conn.close()

def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Retrieve user data based on the username
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()

    conn.close()

    return user_data