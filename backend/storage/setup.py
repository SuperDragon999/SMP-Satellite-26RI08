# Set up SQLite
import sqlite3
import pandas as pd
import json

# Data Logs
database = sqlite3.connect("backend/storage/data/logs.db")
c = database.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS data(
          ID INTEGER PRIMARY KEY,
          type TEXT,
          data1 INTEGER,
          data2 INTEGER,
          snr FLOAT
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS ctrl(
          record INTEGER
);
''')

query = "SELECT COUNT(*) FROM ctrl"
data = pd.read_sql(query, database)
ctrl_size = int(data.iloc[0, 0])

if ctrl_size == 0:
    x = 0  # default recording status is 0
    c.execute('''
    INSERT INTO ctrl VALUES (?);
    ''', (x, ))

database.commit()
database.close()