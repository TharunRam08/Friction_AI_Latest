# backend/data/canary_db.py
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_canary_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    # 1. Canary Config
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canary_config (
        id INTEGER PRIMARY KEY,
        running INTEGER DEFAULT 0,
        interval_minutes INTEGER DEFAULT 1,
        last_run TEXT,
        next_run TEXT
    )""")
    
    # Insert default config if empty
    cursor.execute("SELECT COUNT(*) FROM canary_config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO canary_config (id, running, interval_minutes, last_run, next_run) VALUES (1, 0, 1, NULL, NULL)")
        
    # 2. Canary Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canary_logs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        duration_ms REAL,
        success INTEGER,
        summary TEXT,
        details TEXT
    )""")
    
    # 3. Canary Failure Library
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canary_failure_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        implicated_metrics TEXT,
        historical_pattern TEXT
    )""")
    
    # Seed default failure library entry if empty
    cursor.execute("SELECT COUNT(*) FROM canary_failure_library")
    if cursor.fetchone()[0] == 0:
        # Seed an inventory depletion and support load ticket failure
        cursor.execute("""
        INSERT INTO canary_failure_library (title, description, implicated_metrics, historical_pattern)
        VALUES (?, ?, ?, ?)
        """, (
            "Inventory depletion & Support Spike Failure",
            "Critical hardware inventory depletion combined with a high support ticket volume spike, causing delivery delays and low customer satisfaction.",
            "qty_on_hand,reorder_point,tickets",
            json.dumps({
                "qty_on_hand": 10.0,
                "reorder_point": 25.0,
                "tickets": 8.0
            })
        ))
        
    # 4. Canary Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canary_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headline TEXT,
        solution TEXT,
        evidence TEXT,
        severity TEXT,
        mode TEXT,
        timestamp TEXT,
        status TEXT DEFAULT 'Active',
        feedback TEXT DEFAULT 'None'
    )""")
    
    # Run migration to add solution column if table already exists
    try:
        cursor.execute("ALTER TABLE canary_alerts ADD COLUMN solution TEXT")
    except sqlite3.OperationalError:
        pass
    
    # 5. Canary Checkpoints for Incremental Scanning
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canary_checkpoints (
        table_name TEXT PRIMARY KEY,
        last_scanned_at TEXT
    )""")
    
    conn.commit()
    conn.close()

# Auto-initialize on import
init_canary_db()

# DB Helper functions
def get_canary_config():
    conn = get_conn()
    row = conn.execute("SELECT * FROM canary_config WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else {}

def update_canary_config(running: int, interval_minutes: int, last_run: str = None, next_run: str = None):
    conn = get_conn()
    conn.execute("""
    UPDATE canary_config
    SET running = ?, interval_minutes = ?, last_run = ?, next_run = ?
    WHERE id = 1
    """, (running, interval_minutes, last_run, next_run))
    conn.commit()
    conn.close()

def log_canary_run(timestamp: str, duration_ms: float, success: int, summary: str, details: str):
    conn = get_conn()
    conn.execute("""
    INSERT INTO canary_logs (timestamp, duration_ms, success, summary, details)
    VALUES (?, ?, ?, ?, ?)
    """, (timestamp, duration_ms, success, summary, details))
    conn.commit()
    conn.close()

def get_canary_logs(limit=50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM canary_logs ORDER BY run_id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_failure_library():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM canary_failure_library ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_failure_entry(title: str, description: str, implicated_metrics: str, historical_pattern: str):
    conn = get_conn()
    conn.execute("""
    INSERT INTO canary_failure_library (title, description, implicated_metrics, historical_pattern)
    VALUES (?, ?, ?, ?)
    """, (title, description, implicated_metrics, historical_pattern))
    conn.commit()
    conn.close()

def get_canary_alerts(limit=50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM canary_alerts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_canary_alert(headline: str, solution: str, evidence: str, severity: str, mode: str, timestamp: str):
    conn = get_conn()
    conn.execute("""
    INSERT INTO canary_alerts (headline, solution, evidence, severity, mode, timestamp, status, feedback)
    VALUES (?, ?, ?, ?, ?, ?, 'Active', 'None')
    """, (headline, solution, evidence, severity, mode, timestamp))
    conn.commit()
    conn.close()

def update_alert_feedback(alert_id: int, feedback: str):
    conn = get_conn()
    conn.execute("UPDATE canary_alerts SET feedback = ? WHERE id = ?", (feedback, alert_id))
    # If accurate, we optionally append it to the failure library
    if feedback == 'Accurate':
        alert = conn.execute("SELECT * FROM canary_alerts WHERE id = ?", (alert_id,)).fetchone()
        if alert:
            # Reconstruct simple metrics profile from evidence
            add_failure_entry(
                f"User-Confirmed Failure Alert #{alert['id']}",
                alert['headline'],
                "qty_on_hand,reorder_point,tickets", # Map to safety metrics by default
                alert['evidence']
            )
    conn.commit()
    conn.close()

def resolve_canary_alert(alert_id: int):
    conn = get_conn()
    conn.execute("UPDATE canary_alerts SET status = 'Resolved' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def delete_canary_alert(alert_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM canary_alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def get_checkpoint(table_name: str) -> str:
    conn = get_conn()
    row = conn.execute("SELECT last_scanned_at FROM canary_checkpoints WHERE table_name = ?", (table_name,)).fetchone()
    conn.close()
    return row[0] if row else "1970-01-01"

def update_checkpoint(table_name: str, last_scanned_at: str):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO canary_checkpoints (table_name, last_scanned_at) VALUES (?, ?)", (table_name, last_scanned_at))
    conn.commit()
    conn.close()
