import sqlite3
import json
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="data/database/cleangenius.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._conn()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS scan_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                scan_type TEXT,
                status TEXT DEFAULT 'running',
                total_files INTEGER DEFAULT 0,
                total_size_bytes INTEGER DEFAULT 0,
                progress INTEGER DEFAULT 0,
                message TEXT,
                error TEXT,
                results_json TEXT
            );

            CREATE TABLE IF NOT EXISTS scanned_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                file_path TEXT,
                category TEXT,
                size_bytes INTEGER,
                last_accessed TEXT,
                last_modified TEXT,
                created TEXT,
                ai_safety_score INTEGER,
                ai_recommendation TEXT,
                ai_reasoning TEXT,
                FOREIGN KEY (session_id) REFERENCES scan_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS cleanup_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_session_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'running',
                files_deleted INTEGER DEFAULT 0,
                space_freed_bytes INTEGER DEFAULT 0,
                progress INTEGER DEFAULT 0,
                message TEXT,
                error TEXT,
                FOREIGN KEY (scan_session_id) REFERENCES scan_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS deleted_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cleanup_session_id INTEGER,
                original_path TEXT,
                backup_path TEXT,
                size_bytes INTEGER,
                deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                can_restore INTEGER DEFAULT 1,
                FOREIGN KEY (cleanup_session_id) REFERENCES cleanup_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                provider TEXT,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost_usd REAL,
                request_type TEXT
            );

            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT,
                title TEXT,
                detail TEXT
            );
        """)
        conn.commit()
        conn.close()

    def create_scan_session(self, mode):
        conn = self._conn()
        cur = conn.execute("INSERT INTO scan_sessions (scan_type, status) VALUES (?, 'running')", (mode,))
        conn.commit()
        sid = cur.lastrowid
        conn.close()
        return sid

    def update_scan_progress(self, sid, progress, message=''):
        conn = self._conn()
        conn.execute("UPDATE scan_sessions SET progress=?, message=? WHERE id=?", (progress, message, sid))
        conn.commit()
        conn.close()

    def store_scan_results(self, sid, results):
        conn = self._conn()
        conn.execute(
            "UPDATE scan_sessions SET total_files=?, total_size_bytes=?, results_json=? WHERE id=?",
            (results.get("total_files", 0), results.get("total_size_bytes", 0), json.dumps({
                k: results[k] for k in results if k != "files"
            }), sid)
        )
        for f in results.get("files", [])[:50000]:
            conn.execute(
                """INSERT INTO scanned_files (session_id, file_path, category, size_bytes, last_accessed, last_modified, created)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sid, f.get("path") or f.get("file_path"), f.get("category"), f.get("size_bytes", 0),
                 str(f.get("last_accessed", "")), str(f.get("last_modified", "")), str(f.get("created", "")))
            )
        conn.commit()
        conn.close()

    def store_ai_recommendations(self, sid, recs):
        conn = self._conn()
        conn.execute("INSERT INTO activity (type, title, detail) VALUES (?, ?, ?)",
                     ("ai", "AI Analysis Completed", f"Generated recommendations for scan {sid}"))
        conn.commit()
        conn.close()

    def complete_scan_session(self, sid, results):
        conn = self._conn()
        conn.execute("UPDATE scan_sessions SET status='completed', progress=100 WHERE id=?", (sid,))
        conn.execute("INSERT INTO activity (type, title, detail) VALUES (?, ?, ?)",
                     ("scan", "Scan Completed", f"Found {results.get('total_size_gb', 0):.2f} GB of clearable files"))
        conn.commit()
        conn.close()

    def fail_scan_session(self, sid, err):
        conn = self._conn()
        conn.execute("UPDATE scan_sessions SET status='failed', error=? WHERE id=?", (err, sid))
        conn.commit()
        conn.close()

    def cancel_scan_session(self, sid):
        conn = self._conn()
        conn.execute("UPDATE scan_sessions SET status='cancelled' WHERE id=?", (sid,))
        conn.commit()
        conn.close()

    def get_scan_session(self, sid):
        conn = self._conn()
        row = conn.execute("SELECT * FROM scan_sessions WHERE id=?", (sid,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("results_json"):
            d.update(json.loads(d["results_json"]))
        return d

    def get_latest_scan(self):
        conn = self._conn()
        row = conn.execute("SELECT * FROM scan_sessions WHERE status='completed' ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("results_json"):
            d.update(json.loads(d["results_json"]))
        return d

    def get_files_for_cleanup(self, scan_id, categories=None, file_ids=None):
        conn = self._conn()
        if file_ids:
            q = f"SELECT * FROM scanned_files WHERE id IN ({','.join('?'*len(file_ids))})"
            rows = conn.execute(q, file_ids).fetchall()
        elif categories:
            q = f"SELECT * FROM scanned_files WHERE session_id=? AND category IN ({','.join('?'*len(categories))})"
            rows = conn.execute(q, [scan_id, *categories]).fetchall()
        else:
            rows = conn.execute("SELECT * FROM scanned_files WHERE session_id=?", (scan_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_cleanup_session(self, scan_id):
        conn = self._conn()
        cur = conn.execute("INSERT INTO cleanup_sessions (scan_session_id, status) VALUES (?, 'running')", (scan_id,))
        conn.commit()
        cid = cur.lastrowid
        conn.close()
        return cid

    def update_cleanup_progress(self, cid, progress, message=''):
        conn = self._conn()
        conn.execute("UPDATE cleanup_sessions SET progress=?, message=? WHERE id=?", (progress, message, cid))
        conn.commit()
        conn.close()

    def complete_cleanup_session(self, cid, result):
        conn = self._conn()
        conn.execute(
            "UPDATE cleanup_sessions SET status='completed', files_deleted=?, space_freed_bytes=?, progress=100 WHERE id=?",
            (result.get("files_deleted", 0), result.get("space_freed_bytes", 0), cid)
        )
        conn.execute("INSERT INTO activity (type, title, detail) VALUES (?, ?, ?)",
                     ("cleanup", "Cleanup Completed", f"Freed {result.get('space_freed_gb', 0):.2f} GB"))
        conn.commit()
        conn.close()

    def fail_cleanup_session(self, cid, err):
        conn = self._conn()
        conn.execute("UPDATE cleanup_sessions SET status='failed', error=? WHERE id=?", (err, cid))
        conn.commit()
        conn.close()

    def get_cleanup_session(self, cid):
        conn = self._conn()
        row = conn.execute("SELECT * FROM cleanup_sessions WHERE id=?", (cid,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def mark_cleanup_rolled_back(self, cid):
        conn = self._conn()
        conn.execute("UPDATE cleanup_sessions SET status='rolled_back' WHERE id=?", (cid,))
        conn.execute("INSERT INTO activity (type, title, detail) VALUES (?, ?, ?)",
                     ("rollback", "Cleanup Rolled Back", f"Restored files from cleanup session {cid}"))
        conn.commit()
        conn.close()

    def get_recent_activity(self, limit=10):
        conn = self._conn()
        rows = conn.execute("SELECT * FROM activity ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
