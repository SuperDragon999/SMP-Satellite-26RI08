import sqlite3, json
import pandas as pd
from pathlib import Path

def get_runtime_db_context():
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent
    config_path = project_root / "config.json"
    
    db_name = "telemetry_default"
    if config_path.exists():
        with open(config_path, "r") as f:
            try:
                config = json.load(f)
                db_name = config.get("db_name", db_name)
            except json.JSONDecodeError:
                pass
                
    db_path = project_root / "backend" / "storage" / "data" / f"{db_name}.db"
    
    # Introspect phase dynamically out of the active file context
    phase = 1
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            res = conn.execute("SELECT phase FROM ctrl LIMIT 1;").fetchone()
            if res:
                phase = res[0]
            conn.close()
        except sqlite3.Error:
            pass
            
    return db_path, phase

# db functions
def get_mode():
    '''
    Get recording mode
    '''

    db_path, _ = get_runtime_db_context()
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

    db_path, _ = get_runtime_db_context()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
    UPDATE ctrl SET mode = ?;
    ''', (mode,))
    database.commit()
    database.close()

def addEntry(id, t, d1, d2, s):
    '''
    Add entry to the 'data' table, auto-detects the phase of the experiment
    '''

    db_path, phase = get_runtime_db_context()
    database = sqlite3.connect(db_path)
    c = database.cursor()

    if phase == 1:
        c.execute('''
            INSERT INTO data (ID, type, data1, data2, snr)
                VALUES (?, ?, ?, ?, ?);
        ''', (id, t, d1, d2, s))
    elif phase == 2:
        c.execute('''
            INSERT INTO data (ID, type, data1, data2, status)
                VALUES (?, ?, ?, ?, ?);
        ''', (id, t, d1, d2, s))

    # Addition done here is shown since this is displayed in terminal
    print(f"Added into 'data' table {id}, {t}, {d1}, {d2}, {s}.")

    database.commit()
    database.close()

def deleteEntry(id, t, d1, d2, s):
    '''
    Deletes specified entry from 'data' table, auto-detects the phase of the experiment
    '''

    db_path, phase = get_runtime_db_context()
    database = sqlite3.connect(db_path)
    c = database.cursor()

    if phase == 1:
        c.execute('''
            DELETE FROM data WHERE ID = ? AND type = ? AND data1 = ? AND data2 = ? AND snr = ?;
        ''', (id, t, d1, d2, s))
    elif phase == 2:
        c.execute('''
            DELETE FROM data WHERE ID = ? AND type = ? AND data1 = ? AND data2 = ? AND status = ?;
        ''', (id, t, d1, d2, s))    

    database.commit()
    database.close()

def addProcessing(id, t):
    db_path, _ = get_runtime_db_context()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        INSERT INTO processing (ID, time) VALUES (?, ?);
    ''', (id, t))

    print(f"Added into 'processing' {id}, {t}")
    database.commit()
    database.close()

def deleteProcessing(id, t):
    '''
    Deletes specified entry from 'processing' table
    '''

    db_path, _ = get_runtime_db_context()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    c.execute('''
        DELETE FROM processing WHERE ID = ? AND time = ?;
    ''', (id, t))

    database.commit()
    database.close()

def readAllData():
    '''
    Read all data in table
    '''

    db_path, _ = get_runtime_db_context()
    record_mode = get_mode()
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM processing;" if record_mode else "SELECT * FROM data;"
    data = pd.read_sql(query, conn)
    return data

def getData(columns, getFail):
    '''
    Selectively get columns from tables. If getFail is true, failed packets will be included, and vice versa.
    '''

    db_path, _ = get_runtime_db_context()
    conn = sqlite3.connect(db_path)
    
    escaped_columns = [f"[{col}]" if " " in col else col for col in columns]
    column_string = ", ".join(escaped_columns)

    record_mode = get_mode()
    if not getFail: # not getFail means you don't want failed packets, so there is selection here
        if record_mode == 0:
            query = f"SELECT {column_string} FROM data WHERE type = 'PACKET';"
        elif record_mode == 1:
            query = f"SELECT {column_string} FROM processing WHERE ID != -1;"
    else:
        if record_mode == 0:
            query = f"SELECT {column_string} FROM data;"
        elif record_mode == 1:
            query = f"SELECT {column_string} FROM processing;"
    data = pd.read_sql(query, conn)
    return data

def clearData():
    '''
    Clear all data, depends on which mode you are using. SAT mode clears the 'processing' table, GND mode clears the 'data' table.
    Respective empty tables will be regenerated based on the phase of the experimentation.
    '''

    db_path, phase = get_runtime_db_context()
    record_mode = get_mode()
    database = sqlite3.connect(db_path)
    c = database.cursor()
    if record_mode == 0:
        c.execute('''
            DROP TABLE data;
        ''')
        if phase == 1:
            c.execute('''
            CREATE TABLE IF NOT EXISTS data(
                    ID INTEGER,
                    type TEXT,
                    data1 INTEGER,
                    data2 INTEGER,
                    snr FLOAT
            );
            ''')
        elif phase == 2:
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

def count(val, column):
    '''
    Get number of occurences of a value in a column.
    '''

    db_path, _ = get_runtime_db_context()
    record_mode = get_mode()
    conn = sqlite3.connect(db_path)
    query = f"SELECT COUNT(*) FROM data WHERE {column} = {val};" if record_mode == 0 else f"SELECT COUNT(*) FROM processing WHERE {column} = {val};"
    result = conn.execute(query)
    return result.fetchone()[0]

def set_record(mode):
    '''
    Enable/disable recording on the frontend
    '''

    db_path, _ = get_runtime_db_context()
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

    db_path, _ = get_runtime_db_context()
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