import os
import psutil
from typing import Dict, List

PROTECTED_PATHS = [
    r"C:\Windows\System32",
    r"C:\Windows\SysWOW64",
    r"C:\Windows\WinSxS",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
]

class SafetyManager:
    def __init__(self, config=None):
        self.config = config

    def check_files(self, files: List[dict]) -> Dict:
        blocked = []
        warnings = []
        safe_files = []

        for f in files:
            path = f.get("file_path") or f.get("path", "")
            if not path:
                continue

            norm_path = os.path.normpath(path).lower()
            is_blocked = False

            # Check critical paths
            for prot in PROTECTED_PATHS:
                if norm_path.startswith(os.path.normpath(prot).lower()):
                    blocked.append({"path": path, "reason": "Protected system path"})
                    is_blocked = True
                    break

            if is_blocked:
                continue

            # Check if file is currently open by trying to open it exclusively if needed,
            # avoiding psutil.process_iter(['open_files']) which is extremely slow on Windows
            if self._is_file_locked(path):
                blocked.append({"path": path, "reason": "File is currently in use"})
                is_blocked = True
                continue

            safe_files.append(f)

        return {
            "safe": len(blocked) == 0,
            "has_safe_files": len(safe_files) > 0 or len(files) == 0,
            "safe_files": safe_files,
            "blocked_files": blocked,
            "warnings": warnings,
            "checked_count": len(files)
        }

    def _is_file_locked(self, file_path: str) -> bool:
        if not os.path.isfile(file_path):
            return False
        # If running under test mock mode, bypass process lock check
        if os.getenv("MOCK_WINDOWS") == "true":
            return False
        try:
            with open(file_path, "rb"):
                pass
            return False
        except (PermissionError, OSError):
            return True
