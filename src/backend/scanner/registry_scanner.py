import os
import platform
from typing import Callable, Dict, List, Optional

class RegistryScanner:
    def scan(self, progress_cb: Optional[Callable] = None) -> Dict:
        findings: List[dict] = []
        is_win = platform.system() == "Windows" and os.getenv("MOCK_WINDOWS", "false").lower() != "true"

        if is_win:
            try:
                import winreg
                JUNK_KEYS = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"),
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"),
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"),
                ]
                for i, (hive, subkey) in enumerate(JUNK_KEYS):
                    try:
                        key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ)
                        n_vals, n_keys, _ = winreg.QueryInfoKey(key)
                        findings.append({
                            "hive": "HKCU",
                            "path": subkey,
                            "value_count": n_vals,
                            "subkey_count": n_keys,
                            "category": "registry_junk",
                            "safety_score": 8,
                            "action": "review",
                        })
                        winreg.CloseKey(key)
                    except OSError:
                        continue
                    if progress_cb:
                        progress_cb(i + 1, len(JUNK_KEYS), "Scanning registry...")
            except Exception:
                pass
        else:
            # Mock registry findings for non-Windows or testing
            findings = [
                {
                    "hive": "HKCU",
                    "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
                    "value_count": 14,
                    "subkey_count": 2,
                    "category": "registry_junk",
                    "safety_score": 8,
                    "action": "review",
                },
                {
                    "hive": "HKCU",
                    "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                    "value_count": 5,
                    "subkey_count": 0,
                    "category": "registry_junk",
                    "safety_score": 9,
                    "action": "delete",
                }
            ]
            if progress_cb:
                progress_cb(1, 1, "Mock registry scan completed")

        return {
            "files": [],
            "registry": findings,
            "total_files": 0,
            "total_size_gb": 0,
            "categories": {"registry_junk": {"count": len(findings), "size_bytes": 0}},
            "mode": "registry",
        }
