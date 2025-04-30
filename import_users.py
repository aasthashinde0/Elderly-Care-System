import sqlite3
import pandas as pd

# Load your CSV
df = pd.read_csv("E:/dt_acc/daily_reminder.csv")

# Extract unique user IDs
user_ids = df['Device-ID/User-ID'].unique()

# Connect to the SQLite database
conn = sqlite3.connect("elderly.db")
cursor = conn.cursor()

# Insert users into the users table
for user_id in user_ids:
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, password) VALUES (?, ?)", (user_id, 'defaultpass'))
    except Exception as e:
        print(f"Error inserting user {user_id}: {e}")

conn.commit()
conn.close()

print("✅ All users inserted successfully!")
