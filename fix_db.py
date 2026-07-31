import sqlite3

def fix_database():
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    
    print("Updating mood table...")
    
    # 1. Drop the old table
    cursor.execute("DROP TABLE IF EXISTS mood")
    
    # 2. Create the new table with the 'date' column
    cursor.execute("""
        CREATE TABLE mood (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database repaired! You can now run your app.py")

if __name__ == "__main__":
    fix_database()
