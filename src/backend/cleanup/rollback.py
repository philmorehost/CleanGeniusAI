import os
import shutil
import json
from pathlib import Path

class RollbackManager:
    def __init__(self, db):
        self.db = db
        self.recovery_base = Path(os.getenv("APPDATA", os.path.expanduser("~"))) / "CleanGeniusAI" / "Recovery"
        self.recovery_base.mkdir(parents=True, exist_ok=True)

    def create_restore_point(self, cleanup_id: int, files: list) -> bool:
        session_dir = self.recovery_base / str(cleanup_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        conn = self.db._conn()
        manifest = []

        for f in files:
            orig = f.get("file_path") or f.get("path")
            size = f.get("size_bytes", 0)
            if not orig or not os.path.exists(orig) or not os.path.isfile(orig):
                continue

            fid = f.get("id", len(manifest) + 1)
            filename = os.path.basename(orig)
            backup_file = session_dir / f"{fid}_{filename}"

            try:
                shutil.copy2(orig, backup_file)
                conn.execute(
                    "INSERT INTO deleted_files (cleanup_session_id, original_path, backup_path, size_bytes) VALUES (?, ?, ?, ?)",
                    (cleanup_id, orig, str(backup_file), size)
                )
                manifest.append({"original": orig, "backup": str(backup_file)})
            except Exception:
                continue

        conn.commit()
        conn.close()

        with open(session_dir / "manifest.json", "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, indent=2)

        return True

    def rollback(self, cleanup_id: int) -> dict:
        conn = self.db._conn()
        rows = conn.execute("SELECT * FROM deleted_files WHERE cleanup_session_id=? AND can_restore=1", (cleanup_id,)).fetchall()

        restored = 0
        for r in rows:
            orig, bak = r["original_path"], r["backup_path"]
            try:
                if bak and os.path.exists(bak):
                    Path(orig).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bak, orig)
                    restored += 1
            except Exception:
                continue

        conn.close()
        return {"success": True, "files_restored": restored}
