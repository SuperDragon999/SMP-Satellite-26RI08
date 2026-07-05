import sqlite3

# Data logs setup
def setup(db, type):
    c = db.cursor()

    if type == 1:
        c.execute('''
        CREATE TABLE IF NOT EXISTS data(
                ID INTEGER,
                type TEXT,
                data1 INTEGER,
                data2 INTEGER,
                snr FLOAT
        );
        ''')
    elif type == 2:
        c.execute('''
        CREATE TABLE IF NOT EXISTS data(
                ID INTEGER,
                type TEXT,
                data1 INTEGER,
                data2 INTEGER,
                status INTEGER
        );
        ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS processing (
            ID INTEGER,
            time INTEGER
    );
    ''')

    # 0 means not recording, 1 means recording
    # 0 means GND mode, 1 means SAT mode
    c.execute('''
    CREATE TABLE IF NOT EXISTS ctrl(
            record INTEGER,
            mode INTEGER
    );
    ''')

    query = "SELECT COUNT(*) FROM ctrl"
    result = c.execute(query)
    ctrl_size = result.fetchone()[0]

    if ctrl_size == 0:
        # Default recording status is 0, recording mode is ground
        c.execute('''
        INSERT INTO ctrl VALUES (?, ?);
        ''', (0, 0))

    db.commit()
    db.close()