import os
import pathlib
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
import json

DEFAULT_TEMP_PATHS = [
    os.environ.get("TEMP", ""),
    os.environ.get("TMP", ""),
    r"C:\Windows\Temp",
    os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
    os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
    os.path.expandvars(r"%LOCALAPPDATA%\npm-cache"),
    os.path.expandvars(r"%USERPROFILE%\.cache"),
]

DEV_PATTERNS = {
    "node_modules", ".next", "__pycache__", ".pytest_cache", "target",
    "dist", "build", ".gradle", ".nuget", "bin", "obj", ".vs"
}

PROTECTED = {
    r"C:\Windows\System32",
    r"C:\Windows\SysWOW64",
    r"C:\Windows\WinSxS",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
}

def _is_protected(path: str) -> bool:
    if not path:
        return False
    p = os.path.normpath(path).lower()
    return any(p.startswith(os.path.normpath(x).lower()) for x in PROTECTED)

class DiskScanner:
    def __init__(self, config=None):
        self.config = config

    def categorize(self, file_path: str) -> str:
        name = pathlib.Path(file_path).name.lower()
        parts = pathlib.Path(file_path).parts
        if any(p in DEV_PATTERNS for p in parts):
            return "dev_cache"
        if "cache" in file_path.lower() and any(b in file_path.lower() for b in ("chrome", "firefox", "edge", "brave")):
            return "browser_cache"
        if name.endswith((".tmp", ".temp", ".log")) or "\\temp\\" in file_path.lower() or "/temp/" in file_path.lower():
            return "temp_files"
        if name.endswith((".log", ".etl")):
            return "log_files"
        if name.endswith((".msi", ".iso", ".dmg", ".pkg")):
            return "installers"
        return "miscellaneous"

    def scan(
        self,
        mode: str = "fast",
        paths: Optional[List[str]] = None,
        options: Optional[dict] = None,
        progress_cb: Optional[Callable] = None,
    ) -> Dict:
        options = options or {}

        # Target paths resolution
        if mode == "custom" and paths:
            roots = paths
        elif mode == "deep":
            user_home = os.path.expanduser("~")
            roots = [
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "AppData", "Local", "Temp") if os.name == 'nt' else os.environ.get("TEMP", "/tmp"),
                os.environ.get("TEMP", "/tmp")
            ]
            if paths:
                roots.extend(paths)
        else:
            roots = [p for p in DEFAULT_TEMP_PATHS if p]
            if not roots:
                roots = [os.environ.get("TEMP", "/tmp")]

        files: List[dict] = []
        skipped = 0
        max_files = options.get("max_files", 50000)
        min_age_days = options.get("min_age_days", 0)
        cutoff = datetime.now() - timedelta(days=min_age_days) if min_age_days else None

        valid_roots = []
        for root in roots:
            if not root or not os.path.exists(root) or _is_protected(root):
                continue
            valid_roots.append(root)

        processed = 0
        for root in valid_roots:
            if os.path.isfile(root):
                try:
                    st = os.stat(root)
                    files.append({
                        "path": root,
                        "size_bytes": st.st_size,
                        "last_accessed": datetime.fromtimestamp(st.st_atime).isoformat(),
                        "last_modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(st.st_ctime).isoformat(),
                        "category": self.categorize(root),
                        "age_days": (datetime.now() - datetime.fromtimestamp(st.st_atime)).days,
                    })
                except Exception:
                    skipped += 1
                continue

            for dirpath, dirnames, filenames in os.walk(root, topdown=True):
                if _is_protected(dirpath):
                    dirnames[:] = []
                    continue
                dirnames[:] = [d for d in dirnames if d not in ("WinSxS", "$Recycle.Bin", "System Volume Information")]

                for fn in filenames:
                    if len(files) >= max_files:
                        break
                    fp = os.path.join(dirpath, fn)
                    try:
                        st = os.stat(fp)
                    except (OSError, PermissionError):
                        skipped += 1
                        continue

                    if cutoff:
                        atime = datetime.fromtimestamp(st.st_atime)
                        if atime > cutoff:
                            continue

                    files.append({
                        "path": fp,
                        "size_bytes": st.st_size,
                        "last_accessed": datetime.fromtimestamp(st.st_atime).isoformat(),
                        "last_modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(st.st_ctime).isoformat(),
                        "category": self.categorize(fp),
                        "age_days": (datetime.now() - datetime.fromtimestamp(st.st_atime)).days,
                    })
                    processed += 1
                    if progress_cb and processed % 100 == 0:
                        progress_cb(processed, max_files, f"Scanning {dirpath[:50]}...")
                if len(files) >= max_files:
                    break

        by_cat = {}
        for f in files:
            c = f["category"]
            by_cat.setdefault(c, {"count": 0, "size_bytes": 0})
            by_cat[c]["count"] += 1
            by_cat[c]["size_bytes"] += f["size_bytes"]

        total = sum(f["size_bytes"] for f in files)
        return {
            "files": files,
            "categories": by_cat,
            "total_files": len(files),
            "total_size_bytes": total,
            "total_size_gb": total / (1024 ** 3),
            "skipped": skipped,
            "mode": mode,
        }
