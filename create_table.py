import sqlite3

# This connects to your database file
conn = sqlite3.connect("database/users.db")
cursor = conn.cursor()

# This command builds the structure to save notifications
cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        icon TEXT,
        title TEXT,
        body TEXT,
        time TEXT
    )
""")

conn.commit()
conn.close()
print("Step 1 Complete: The database is now ready to store notifications!")
