# Set up SQLite
import sqlite3

# Data Logs
database = sqlite3.connect("backend/storage/data/logs.db")
c = database.cursor()

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
c.execute('''DROP TABLE ctrl;''')
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

database.commit()
database.close()