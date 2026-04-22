import sqlite3, datetime
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
db_path = project_root / "backend" / "storage" / "data" / "logs.db"

def addEntry(sat, v, t, s):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO data (Satellite, Main_Bus_Voltage, Temperature, Solar_Generation)
              VALUES (?, ?, ?, ?);
    ''', (sat, v, t, s))

    #debug line
    print(f"Added into data table {sat}, {v}, {t}, {s}.")

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

def readAllCmd():
    '''
    Read everything in cmd
    '''
    conn = sqlite3.connect(db_path)

    data = pd.read_sql("""
    SELECT * FROM commands
    """, conn)

    conn.close()
    return data