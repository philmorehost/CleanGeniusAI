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

            # Check if file is currently open by a process
            if self._is_file_in_use(path):
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

    def _is_file_in_use(self, file_path: str) -> bool:
        if not os.path.isfile(file_path):
            return False
        try:
            for proc in psutil.process_iter(['open_files']):
                try:
                    open_files = proc.info.get('open_files') or []
                    for of in open_files:
                        if os.path.normpath(of.path).lower() == os.path.normpath(file_path).lower():
                            return True
                except (psutil.Error, OSError):
                    continue
        except Exception:
            pass
        return False
