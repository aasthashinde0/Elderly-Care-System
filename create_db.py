import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('elderly.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
               ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS health_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    reminder_type TEXT,
    scheduled_datetime TEXT,
    reminder_sent TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS safety_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    location TEXT,
    alert_triggered TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vital_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    heart_rate INTEGER,
    blood_pressure TEXT,
    glucose_level INTEGER,
    alert_triggered TEXT
)
''')

conn.commit()

# Load CSV data
health_df = pd.read_csv("E:/dt_acc/daily_reminder.csv")
safety_df = pd.read_csv("E:/dt_acc/health_monitoring.csv")
reminder_df = pd.read_csv("E:/dt_acc/safety_monitoring.csv")

# Save data into tables
health_df.to_sql('health_reminders', conn, if_exists='replace', index=False)
safety_df.to_sql('health_monitoring', conn, if_exists='replace', index=False)
reminder_df.to_sql('safety_monitoring', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

print("Database created and data inserted successfully!")
