from agents import get_due_reminders, get_fall_alerts, get_health_alerts
from flask import Flask, render_template , request, redirect, url_for, session
import sqlite3
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

# @app.route('/')
# def dashboard():
#     reminders = get_due_reminders()
#     alerts = get_fall_alerts()
#     health_alerts = get_health_alerts()
#     return render_template('dashboard.html', reminders=reminders, alerts=alerts, health_alerts=health_alerts)

# if __name__ == '__main__':
#     app.run(debug=True)

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Needed for sessions

# Dummy users (user_id -> password)
# users = {
#     'D1000': 'pass123',
#     'D1002': 'mypassword',
#     'D1003': '1234'
# }

@app.route('/')
def home():
    return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     user_id = request.form['user_id']
#     password = request.form['password']
#     print(f"Login attempt: {user_id} / {password}")  # 🔍 DEBUG

#     conn = sqlite3.connect('elderly.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE user_id = ? AND password = ?", (user_id, 'password'))
#     user = cursor.fetchone()
#     print("User fetched from DB:", user)
#     conn.close()


#     if user:
#         session['user_id'] = user_id
#         return redirect(url_for('dashboard'))
#     else:
#         return "Invalid Credentials. Please go back and try again."
def fetch_user_from_db(user_id):
    import sqlite3
    conn = sqlite3.connect('elderly.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, password FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']
    print(f"Login attempt: {user_id} / {password}")

    user = fetch_user_from_db(user_id)
    print(f"User fetched from DB: {user}")

    if user and user[1] == password:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Credentials. Please go back and try again."


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']

    # Filter data for only this user
    reminders = get_due_reminders(user_id)
    fall_alerts = get_fall_alerts(user_id)
    health_alerts = get_health_alerts(user_id)

    return render_template('dashboard.html', 
                            reminders=reminders,
                            fall_alerts=fall_alerts,
                            health_alerts=health_alerts)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

#if __name__ == '__main__':
 #   app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
