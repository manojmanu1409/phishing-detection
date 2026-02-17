import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'phishing_app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table for detection logs
    c.execute('''CREATE TABLE IF NOT EXISTS detection_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT,
                  input_data TEXT,
                  prediction TEXT,
                  confidence REAL,
                  timestamp DATETIME)''')
    
    # Table for user feedback
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  log_id INTEGER,
                  is_correct INTEGER,
                  comments TEXT,
                  timestamp DATETIME)''')
    
    conn.commit()
    conn.close()

def log_detection(detection_type, input_data, prediction, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO detection_logs (type, input_data, prediction, confidence, timestamp) VALUES (?, ?, ?, ?, ?)",
              (detection_type, input_data, str(prediction), confidence, datetime.now()))
    conn.commit()
    conn.close()

def get_logs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM detection_logs ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT type, prediction, COUNT(*) as count FROM detection_logs GROUP BY type, prediction", conn)
    conn.close()
    return df
