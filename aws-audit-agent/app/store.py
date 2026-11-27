import json, sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

def _connect():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DATABASE_PATH)
    c.execute("CREATE TABLE IF NOT EXISTS audits (audit_id TEXT PRIMARY KEY, created_at TEXT, status TEXT, payload TEXT)")
    return c

def save_audit(audit_id, payload, status="COMPLETED"):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO audits VALUES (?,?,?,?)",
                  (audit_id, payload.get("started_at"), status, json.dumps(payload, default=str)))

def list_audits():
    with _connect() as c:
        rows = c.execute("SELECT audit_id,created_at,status FROM audits ORDER BY created_at DESC LIMIT 100").fetchall()
    return [{"audit_id":r[0],"created_at":r[1],"status":r[2]} for r in rows]

def get_audit(audit_id):
    with _connect() as c:
        row = c.execute("SELECT payload FROM audits WHERE audit_id=?", (audit_id,)).fetchone()
    return json.loads(row[0]) if row else None
