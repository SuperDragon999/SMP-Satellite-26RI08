import sqlite3
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
db_path = project_root / "backend" / "storage" / "data" / "logs.db"

def addEntry(id, s, l, t):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO data (ID, sensor, latency, type)
              VALUES (?, ?, ?, ?);
    ''', (id, s, l, t))

    #debug line
    print(f"Added into data table {id}, {s}, {l}, {t}.")

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
    
    query = f"SELECT {column_string} FROM data WHERE type != 'DROP';"
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
            latency INTEGER,
            type TEXT
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

def get_telemetry_df():
    '''
    Get jitter and latency from data.
    '''
    conn = sqlite3.connect(db_path)
    
    query = """
    WITH LatencyDelta AS (
        SELECT 
            ID,
            latency,
            LAG(latency) OVER (ORDER BY ID) as prev_latency
        FROM data WHERE type != 'DROP'
    )
    SELECT 
        ID,
        latency,
        CASE 
            WHEN prev_latency IS NULL THEN 0
            ELSE ABS(latency - prev_latency)
        END as jitter
    FROM LatencyDelta
    ORDER BY ID ASC;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

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