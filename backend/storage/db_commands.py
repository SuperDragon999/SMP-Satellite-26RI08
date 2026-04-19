import sqlite3, datetime
import pandas as pd

def addEntry(data, station):
    database = sqlite3.connect("logs/packet_log.db")
    c = database.cursor()

    database.commit()
    database.close()

def getData():
    conn = sqlite3.connect('logs/packet_log.db')

    df = pd.read_sql_query("""
    SELECT timestamp, battery
    FROM telemetry
    ORDER BY timestamp
    """, conn)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    conn.close()