from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from twilio.rest import Client
import sqlite3
import schedule
import time
import threading

app = Flask(__name__)

# Twilio API credentials
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
twilio_whatsapp_number = 'whatsapp:+your_twilio_number'

client = Client(account_sid, auth_token)


# SQLite Database setup
def init_db():
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS birthdays
                      (id INTEGER PRIMARY KEY, name TEXT, date_of_birth TEXT, message TEXT, phone_number TEXT)''')
    conn.commit()
    conn.close()


init_db()  # Initialize the database on app start


# Function to add a birthday
def add_birthday(name, dob, message, phone_number):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO birthdays (name, date_of_birth, message, phone_number) VALUES (?, ?, ?, ?)",
                   (name, dob, message, phone_number))
    conn.commit()
    conn.close()


# Function to update a birthday
def update_birthday(id, name, dob, message, phone_number):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE birthdays SET name = ?, date_of_birth = ?, message = ?, phone_number = ? WHERE id = ?",
                   (name, dob, message, phone_number, id))
    conn.commit()
    conn.close()


# Function to delete a birthday
def delete_birthday(id):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# Function to get all birthdays
def get_birthdays():
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birthdays")
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays


# Function to get a single birthday by ID
def get_birthday(id):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birthdays WHERE id = ?", (id,))
    birthday = cursor.fetchone()
    conn.close()
    return birthday


# Function to send birthday message
def send_birthday_message():
    today = datetime.now().strftime('%m-%d')

    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, message, phone_number FROM birthdays WHERE strftime('%m-%d', date_of_birth) = ?",
                   (today,))
    birthdays_today = cursor.fetchall()

    for birthday in birthdays_today:
        name, message, phone_number = birthday
        message_body = f"Happy Birthday {name}! {message}"
        client.messages.create(
            body=message_body,
            from_=twilio_whatsapp_number,
            to=f'whatsapp:{phone_number}'
        )

    conn.close()


# Schedule the task to check birthdays every day
def schedule_daily_birthday_check():
    schedule.every().day.at("08:00").do(send_birthday_message)

    while True:
        schedule.run_pending()
        time.sleep(60)


# Run scheduler in a separate thread
scheduler_thread = threading.Thread(target=schedule_daily_birthday_check)
scheduler_thread.daemon = True
scheduler_thread.start()


# Routes for the Flask app
@app.route('/')
def index():
    birthdays = get_birthdays()
    return render_template('index.html', birthdays=birthdays)


@app.route('/add_birthday', methods=['POST'])
def add_birthday_route():
    name = request.form['name']
    dob = request.form['dob']
    message = request.form['message']
    phone_number = request.form['phone_number']

    add_birthday(name, dob, message, phone_number)

    return redirect(url_for('success'))


@app.route('/delete_birthday/<int:id>', methods=['POST'])
def delete_birthday_route(id):
    delete_birthday(id)
    return redirect(url_for('index'))


@app.route('/update_birthday/<int:id>', methods=['GET', 'POST'])
def update_birthday_route(id):
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        message = request.form['message']
        phone_number = request.form['phone_number']

        update_birthday(id, name, dob, message, phone_number)
        return redirect(url_for('index'))
    else:
        birthday = get_birthday(id)
        return render_template('update_birthday.html', birthday=birthday)


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == "__main__":
    app.run(debug=True)
