import sqlite3

conn = sqlite3.connect('linkedin_lead_checker.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("✓ Tablas creadas:")
for table in tables:
    print(f"  - {table}")
conn.close()
