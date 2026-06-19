import sqlite3
import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
txt_config_path = project_root / "config.txt"

if txt_config_path.exists():
    with open(txt_config_path, "r") as f:
        db_name = f.read().strip()

db_path = project_root / "backend" / "storage" / "data" / f"{db_name}.db"

# Phase 1 db functions
def get_mode():
    '''
    Get recording mode
    '''

    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
    SELECT mode FROM ctrl LIMIT 1;
    ''')
    state = c.fetchone()
    c.close()
    database.close()
    return state[0]

def set_mode(mode):
    '''
    Set recording mode on the satellite / ground station
    '''

    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
    UPDATE ctrl SET mode = ?;
    ''', (mode,))
    database.commit()
    database.close()

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

def addToA(id, t):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO toa (ID, time) VALUES (?, ?);
    ''', (id, t))

    print(f"Added into toa {id}, {t}")
    database.commit()
    database.close()

def deleteEntry(id, t, d1, d2, s):
    '''
    Deletes specified entry from 'data' table
    '''
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        DELETE FROM data WHERE ID = ? AND type = ? AND data1 = ? AND data2 = ? AND snr = ?;
    ''', (id, t, d1, d2, s))

    database.commit()
    database.close()

def deleteToA(id, t):
    '''
    Deletes specified entry from 'toa' table
    '''
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        DELETE FROM toa WHERE ID = ? AND time = ?;
    ''', (id, t))

    database.commit()
    database.close()


def readAllData():
    '''
    Read all data in table
    '''
    record_mode = get_mode()
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM toa;" if record_mode else "SELECT * FROM data;"
    data = pd.read_sql(query, conn)
    return data

def getData(columns, getFail):
    '''
    Selectively get columns from tables. If getFail is true, failed packets will be included, and vice versa.
    '''
    conn = sqlite3.connect(db_path)
    
    escaped_columns = [f"[{col}]" if " " in col else col for col in columns]
    column_string = ", ".join(escaped_columns)

    record_mode = get_mode()
    if not getFail: # not getFail means you don't want failed packets, so there is selection here
        if record_mode == 0:
            query = f"SELECT {column_string} FROM data WHERE type = 'PACKET';"
        elif record_mode == 1:
            query = f"SELECT {column_string} FROM toa WHERE ID != -1;"
    else:
        if record_mode == 0:
            query = f"SELECT {column_string} FROM data;"
        elif record_mode == 1:
            query = f"SELECT {column_string} FROM toa;"
    data = pd.read_sql(query, conn)
    return data

def clearData():
    '''
    Clear all data, depends on which mode you are using. SAT mode clears the ToA table, GND mode clears the Data table.
    '''
    record_mode = get_mode()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    if record_mode == 0:
        c.execute('''
            DROP TABLE data;
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS data(
                ID INTEGER,
                type TEXT,
                data1 INTEGER,
                data2 INTEGER,
                snr FLOAT
        );
        ''')
    else:
        c.execute('''
            DROP TABLE toa;
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS toa (
                ID INTEGER,
                time INTEGER
        );
        ''')

    database.commit()
    database.close()

def count(val, column):
    '''
    Get number of occurences of a value in a column.
    '''
    record_mode = get_mode()
    conn = sqlite3.connect(db_path)
    query = f"SELECT COUNT(*) FROM data WHERE {column} = {val};" if record_mode == 0 else f"SELECT COUNT(*) FROM toa WHERE {column} = {val};"
    result = conn.execute(query)
    return result.fetchone()[0]

def set_record(mode):
    '''
    Enable/disable recording on the frontend
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

# Phase 2 db functions
def addEntry2(id, t, d1, d2, s):
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO data (ID, type, data1, data2, status)
              VALUES (?, ?, ?, ?, ?);
    ''', (id, t, d1, d2, s))

    #debug line
    print(f"Added into data table {id}, {t}, {d1}, {d2}, {s}.")

    database.commit()
    database.close()

def clearData2():
    '''
    Clear all data, depends on which mode you are using. SAT mode clears the ToA table, GND mode clears the Data table.
    '''
    record_mode = get_mode()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    if record_mode == 0:
        c.execute('''
            DROP TABLE data;
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS data(
                ID INTEGER,
                type TEXT,
                data1 INTEGER,
                data2 INTEGER,
                status INTEGER
        );
        ''')
    else:
        c.execute('''
            DROP TABLE processing;
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS processing (
                ID INTEGER,
                time INTEGER
        );
        ''')

    database.commit()
    database.close()

def deleteEntry2(id, t, d1, d2, s):
    '''
    Deletes specified entry from 'data' table
    '''
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        DELETE FROM data WHERE ID = ? AND type = ? AND data1 = ? AND data2 = ? AND status = ?;
    ''', (id, t, d1, d2, s))

    database.commit()
    database.close()