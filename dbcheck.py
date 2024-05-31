import sqlite3

def fetch_data():
    conn = sqlite3.connect('database.db')  # Connect to the database
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")  # Execute a query
    rows = cur.fetchall()  # Fetch all the results

    for row in rows:
        print(row)  # Print each row

    cur.close()
    conn.close()

fetch_data()  # Call the function
