import sqlite3
import json
import uuid
from datetime import datetime
import os

DB_NAME = "hackforge.db"

def get_db_connection(db_path=DB_NAME):
    # Ensure directory exists if path contains a subdirectory
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT,
        theme TEXT,
        problem_statement TEXT,
        constraints TEXT,
        tech_preferences TEXT,
        status TEXT,
        logs TEXT,
        artifacts TEXT,
        summary TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def create_project(name, theme, problem_statement, constraints, tech_preferences, db_path=DB_NAME):
    project_id = str(uuid.uuid4())
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    
    # Initialize logs as empty array and artifacts as empty dict
    logs = json.dumps([])
    artifacts = json.dumps({})
    summary = ""
    status = "PENDING"
    
    cursor.execute("""
    INSERT INTO projects (id, name, theme, problem_statement, constraints, tech_preferences, status, logs, artifacts, summary, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, name, theme, problem_statement, constraints, tech_preferences, status, logs, artifacts, summary, created_at))
    
    conn.commit()
    conn.close()
    return project_id

def update_project_status(project_id, status, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE projects SET status = ? WHERE id = ?
    """, (status, project_id))
    conn.commit()
    conn.close()

def add_project_log(project_id, agent_name, message, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get current logs
    cursor.execute("SELECT logs FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
        
    logs = json.loads(row['logs'])
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "message": message
    }
    logs.append(log_entry)
    
    cursor.execute("UPDATE projects SET logs = ? WHERE id = ?", (json.dumps(logs), project_id))
    conn.commit()
    conn.close()

def save_project_summary(project_id, summary, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET summary = ? WHERE id = ?", (summary, project_id))
    conn.commit()
    conn.close()

def save_blueprint_artifact(project_id, section_name, content, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get current artifacts
    cursor.execute("SELECT artifacts FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
        
    artifacts = json.loads(row['artifacts'])
    artifacts[section_name] = content
    
    cursor.execute("UPDATE projects SET artifacts = ? WHERE id = ?", (json.dumps(artifacts), project_id))
    conn.commit()
    conn.close()

def get_project(project_id, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def list_projects(db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, theme, problem_statement, status, created_at, summary FROM projects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_project(project_id, db_path=DB_NAME):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
