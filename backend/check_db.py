import sqlite3

# Connect to database
conn = sqlite3.connect('garagereg.db')
cursor = conn.cursor()

# Check existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Existing tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if tickets table exists
try:
    cursor.execute("SELECT COUNT(*) FROM tickets")
    print(f"\nTickets table exists with {cursor.fetchone()[0]} records")
    
    # Check tickets table structure
    cursor.execute("PRAGMA table_info(tickets)")
    columns = cursor.fetchall()
    print("\nTickets table columns:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")
        
except sqlite3.OperationalError:
    print("\nTickets table does not exist")

conn.close()