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

def getData(columns):
    '''
    Selectively get columns from data
    '''
    conn = sqlite3.connect(db_path)
    
    escaped_columns = [f"[{col}]" if " " in col else col for col in columns]
    column_string = ", ".join(escaped_columns)
    
    query = f"SELECT {column_string} FROM data;"
    data = pd.read_sql(query, conn)
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

def set_record(mode):
    '''
    Set recording mode on the satellite network
    '''

    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
    UPDATE ctrl SET record = ?;
    ''', (1 if mode == 1 else 0,))
    database.commit()
    database.close()

def get_record():
    '''
    Get recording state
    '''

    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
    SELECT record FROM ctrl LIMIT 1;
    ''')
    state = c.fetchone()
    c.close()
    database.close()
    if state[0] == 1:
        return True
    return False