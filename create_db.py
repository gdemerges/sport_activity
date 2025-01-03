import sqlite3

db_path = "sport.db"
conn = sqlite3.connect(db_path)

conn.execute("""
CREATE TABLE IF NOT EXISTS cardio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    exercice TEXT NOT NULL,
    distance REAL,
    temps INTEGER,
    commentaires TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS musculation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    exercice TEXT NOT NULL,
    poids REAL,
    series_x_repetitions TEXT,
    commentaires TEXT
)
""")

conn.close()
print("Base de données et tables créées.")
