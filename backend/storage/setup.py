# Run to set up SQLite table

# Data Logs
# Setup for phase 1
def setup(db):
    c = db.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS data(
            ID INTEGER,
            type TEXT,
            data1 INTEGER,
            data2 INTEGER,
            snr FLOAT
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS toa (
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

# Data Logs
# Setup for phase 2
def setup2(db):
    c = db.cursor()

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