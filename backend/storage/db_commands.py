import sqlite3, datetime
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
db_path = project_root / "backend" / "storage" / "data" / "logs.db"

def addEntry(id, s, l):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO data (ID, sensor, latency)
              VALUES (?, ?, ?);
    ''', (id, s, l))

    #debug line
    print(f"Added into data table {id}, {s}, {l}.")

    database.commit()
    database.close()

def readAllData():
    '''
    Read everything in data
    '''
    conn = sqlite3.connect(db_path)

    data = pd.read_sql("""
    SELECT * FROM data
    """, conn)

    conn.close()
    return data

def clearData():
    '''
    Clear all data
    '''

    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        DROP TABLE data;
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS data(
            ID INTEGER PRIMARY KEY,
            sensor INTEGER,
            latency INTEGER
    );
    ''')

    database.commit()
    database.close()