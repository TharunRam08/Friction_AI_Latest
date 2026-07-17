import sqlite3
import os

db_path = r"c:\Users\tharu\Downloads\Friction_AI\FRICTION\backend\data\crm.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- DEALS DATE RANGE ---")
cur.execute("SELECT MIN(close_date), MAX(close_date), COUNT(*) FROM deals")
print(cur.fetchone())

print("\n--- STAGES IN DEALS ---")
cur.execute("SELECT stage, COUNT(*) FROM deals GROUP BY stage")
print(cur.fetchall())

print("\n--- LATEST DEALS ---")
cur.execute("SELECT * FROM deals ORDER BY close_date DESC LIMIT 5")
print(cur.fetchall())

print("\n--- SUPPORT TICKETS DATE RANGE ---")
cur.execute("SELECT MIN(opened_date), MAX(opened_date), COUNT(*) FROM support_tickets")
print(cur.fetchone())

print("\n--- EXPENSES DATE RANGE ---")
cur.execute("SELECT MIN(month), MAX(month), COUNT(*) FROM expenses")
print(cur.fetchone())

conn.close()
