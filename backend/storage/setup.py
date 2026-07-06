# Data logs setup
def setup(db, mode, type):
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
	# 1 means phase 1, 2 means phase 2
	c.execute('''
	CREATE TABLE IF NOT EXISTS ctrl(
			record INTEGER,
			mode INTEGER,
			phase INTEGER
	);
	''')
	c.execute('''
	INSERT INTO ctrl VALUES (?, ?, ?);
	''', (0, mode, type))

	db.commit()
	db.close()