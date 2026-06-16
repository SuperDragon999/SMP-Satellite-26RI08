import sqlite3
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
db_path = project_root / "backend" / "storage" / "data" / "logs.db"

def addEntry(id, t, d1, d2, s):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO data (ID, type, data1, data2, snr)
              VALUES (?, ?, ?, ?, ?);
    ''', (id, t, d1, d2, s))

    #debug line
    print(f"Added into data table {id}, {t}, {d1}, {d2}, {s}.")

    database.commit()
    database.close()

def readAllData():
    '''
    Read all data in table
    '''

    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM data;"
    data = pd.read_sql(query, conn)
    return data

def getData(columns):
    '''
    Selectively get columns from data, not inclusive of dropped packets
    '''
    conn = sqlite3.connect(db_path)
    
    escaped_columns = [f"[{col}]" if " " in col else col for col in columns]
    column_string = ", ".join(escaped_columns)
    
    query = f"SELECT {column_string} FROM data WHERE type != 'LINK_ERR';"
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
            type TEXT,
            data1 INTEGER,
            data2 INTEGER,
            snr FLOAT
    );
    ''')

    database.commit()
    database.close()

def count(val, column):
    '''
    Get number of occurences of a value in a column.
    '''

    conn = sqlite3.connect(db_path)
    query = f"SELECT COUNT(*) FROM data WHERE {column} = {val}"
    data = pd.read_sql(query, conn)
    return int(data.iloc[0, 0])

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