import sqlite3
import pandas as pd 
import numpy as np 
import ollama
from datetime import datetime, timedelta

def get_due_reminders(user_id):
    conn = sqlite3.connect('elderly.db') 
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        SELECT *FROM health_reminders
        WHERE "Device-ID/User-ID" = ? 
        AND "Scheduled Time" <= ?
        AND LOWER("Reminder Type") = 'no'
     ''', (user_id, current_time))

    due_reminders = cursor.fetchall()
    print(due_reminders)

    messages = []
    MAX_REMINDERS = 5  

    for i, (_, row) in enumerate(due_reminders):
        if i >= MAX_REMINDERS:
            print(f"...and {len(due_reminders) - MAX_REMINDERS} more reminders not shown.")
            break

        reminder_id , device_id, reminder_type, scheduled_datetime = row

        message = generate_reminder_message(
        user_id=device_id,
        reminder_type=reminder_type,
        time=scheduled_datetime.strftime("")[1]
        )
        messages.append(f"[User {device_id}] - {message}")

        cursor.execute('''
            UPDATE health_reminders
            SET reminder_sent = 'yes'
            WHERE id = ?
        ''', (reminder_id,))

    conn.commit()
    conn.close()    

    return messages   

def generate_reminder_message(user_id, reminder_type, time):
    prompt = f"""
    You are a caring AI assistant helping an elderly user. Create a friendly, simple reminder message for the user.
    
    Details:
    - Reminder type: {reminder_type}
    - Scheduled time: {time}
    - User ID: {user_id}

    Keep the tone warm, supportive, and easy to understand. Avoid overly technical language.
    """
    
    response = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return response['message']['content']



##########FALL ALERTS AGENT##########
# reminder_df = reminder_df.drop(columns=[col for col in reminder_df.columns if "Unnamed" in col])

def get_fall_alerts(user_id):
    conn = sqlite3.connect('elderly.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM safety_monitoring
        WHERE "Device-ID/User-ID" = ?
        AND (
            LOWER("Fall Detected (Yes/No)") = 'yes'
            OR "Post-Fall Inactivity Duration (Seconds)" > 300
        )
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    messages = []
    MAX_ALERTS = 5

    for i, row in enumerate(rows):
        if i >= MAX_ALERTS:
            messages.append(f"...and {len(rows) - MAX_ALERTS} more alerts not shown.")
            break

        user_id, timestamp, activity, fall_detected, impact, inactivity, location, alert_triggered, caregiver_notified = row
        reason = (
            "Fall detected"
            if fall_detected.lower() == 'yes'
            else "Prolonged inactivity after potential fall"
        )

        message = generate_fall_alert(
            user_id=user_id,
            location=location,
            reason=reason
        )
        messages.append(f"[User {user_id}] at {location}:\n{message}")

    return messages


def generate_fall_alert(user_id, location, reason):
    prompt = f"""
    You are an AI assistant responsible for elderly care alerts.

    Create a concise emergency message for caregivers of user {user_id}.
    The incident happened at {location}.
    Reason: {reason}.

    The tone should be compassionate and urgent, asking for quick attention.
    """
    response = ollama.chat(
        model='mistral', 
        messages=[ {"role": "user", "content": prompt}]
    )
    return response['message']['content']

#######Health MONITORING AGENT##########
#safety_df = safety_df.drop(columns=[col for col in safety_df.columns if "Unnamed" in col])

def get_health_alerts(user_id):
    conn = sqlite3.connect('elderly.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    cursor.execute(''' 
    
        SELECT * FROM health_monitoring
        WHERE "Device-ID/User-ID" = ?   
            AND (
            LOWER("Heart Rate Below/Above Threshold (Yes/No)") = 'yes'
            OR LOWER("Blood Pressure Below/Above Threshold (Yes/No)") = 'yes'
            OR LOWER("Glucose Levels Below/Above Threshold (Yes/No)") = 'yes'
            OR LOWER("SpO₂ Below Threshold (Yes/No)") = 'yes'
        )
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    messages = []
    MAX_ALERTS = 10  

    for i, row in enumerate(rows):
        if i >= MAX_ALERTS:
            messages.append(f"...and {len(rows) - MAX_ALERTS} more alerts not shown.")
            break

        alert = generate_health_alert(row)
        if alert:
            messages.append(alert)
    
    return messages

def generate_health_alert(row):
    """Generates health alert message based on abnormal readings."""
    user_id = row['Device-ID/User-ID']
    alert_parts = []

    if row['Heart Rate Below/Above Threshold (Yes/No)'].lower() == 'yes':
        alert_parts.append(f"- Abnormal heart rate detected: {row['Heart Rate']} bpm.")
    
    if row['Blood Pressure Below/Above Threshold (Yes/No)'].lower() == 'yes':
        alert_parts.append(f"- Blood pressure reading is concerning: {row['Blood Pressure']}.")
    
    if row['Glucose Levels Below/Above Threshold (Yes/No)'].lower() == 'yes':
        alert_parts.append(f"- Irregular glucose level: {row['Glucose Levels']} mg/dL.")
    
    if row['SpO₂ Below Threshold (Yes/No)'].lower() == 'yes':
        alert_parts.append(f"- Low oxygen saturation: {row['Oxygen Saturation (SpO₂%)']}%.")

    if not alert_parts:
        return None  # No issues detected

    message = f"""
🚨 Urgent Health Alert for User {user_id} 🚨

Dear Caregiver,

The health monitoring system has detected the following irregularities:

{chr(10).join(alert_parts)}

Please check on user {user_id} immediately and consider seeking medical attention if symptoms persist.

Best regards,  
Vital Health Monitoring Agent
"""
    return message


