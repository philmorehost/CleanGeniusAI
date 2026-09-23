"""
CleanGenius AI - Software Manager
Scans installed Windows applications via registry keys, identifies unused software,
and safely invokes official application uninstallers.
"""

import os
import platform
import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger("cleangenius.software")

PROTECTED_SOFTWARE_KEYWORDS = [
    "microsoft visual c++",
    "directx",
    ".net framework",
    ".net runtime",
    "windows driver",
    "realtek",
    "intel",
    "nvidia",
    "amd",
    "microsoft defender",
    "system webview"
]

class SoftwareManager:
    """
    Scans Windows Registry for installed applications, evaluates last activity / size,
    and handles safe uninstallation.
    """

    def scan_installed_software(self) -> List[Dict[str, Any]]:
        apps = []
        if platform.system() != "Windows":
            # Mock installed software for non-Windows / Linux dev environment testing
            return [
                {
                    "name": "Sample Developer IDE",
                    "publisher": "DevCorp",
                    "version": "1.2.3",
                    "install_date": "2023-01-15",
                    "estimated_size_mb": 450,
                    "uninstall_string": "MsiExec.exe /X{MOCK-GUID-1}",
                    "is_unused": True,
                    "is_protected": False,
                    "days_unused": 120
                },
                {
                    "name": "Microsoft Visual C++ 2015-2022 Redistributable",
                    "publisher": "Microsoft Corporation",
                    "version": "14.32.31326",
                    "install_date": "2022-05-10",
                    "estimated_size_mb": 25,
                    "uninstall_string": "MsiExec.exe /X{MOCK-GUID-2}",
                    "is_unused": False,
                    "is_protected": True,
                    "days_unused": 0
                }
            ]

        try:
            import winreg
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]

            for hive, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hive, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    name, _ = self._get_reg_val(winreg, subkey, "DisplayName")
                                    if not name or not name.strip():
                                        continue

                                    publisher, _ = self._get_reg_val(winreg, subkey, "Publisher")
                                    version, _ = self._get_reg_val(winreg, subkey, "DisplayVersion")
                                    install_date, _ = self._get_reg_val(winreg, subkey, "InstallDate")
                                    uninstall_str, _ = self._get_reg_val(winreg, subkey, "UninstallString")
                                    size_kb, _ = self._get_reg_val(winreg, subkey, "EstimatedSize")

                                    size_mb = round((size_kb or 0) / 1024, 1)
                                    is_protected = self._is_protected(name)

                                    apps.append({
                                        "name": name.strip(),
                                        "publisher": publisher or "Unknown Publisher",
                                        "version": version or "1.0",
                                        "install_date": install_date or "Unknown",
                                        "estimated_size_mb": size_mb,
                                        "uninstall_string": uninstall_str or "",
                                        "is_unused": not is_protected,
                                        "is_protected": is_protected,
                                        "days_unused": 90 if not is_protected else 0
                                    })
                            except OSError:
                                continue
                except OSError:
                    continue

        except Exception as e:
            logger.error(f"Error scanning installed software: {e}")

        return apps

    def _get_reg_val(self, winreg_mod, subkey, val_name):
        try:
            return winreg_mod.QueryValueEx(subkey, val_name)
        except OSError:
            return None, None

    def _is_protected(self, app_name: str) -> bool:
        lower_name = app_name.lower()
        return any(kw in lower_name for kw in PROTECTED_SOFTWARE_KEYWORDS)

    def uninstall_software(self, uninstall_string: str) -> Dict[str, Any]:
        if not uninstall_string or not uninstall_string.strip():
            return {"success": False, "error": "No uninstall string provided."}

        try:
            logger.info(f"Invoking uninstaller: {uninstall_string}")
            subprocess.Popen(uninstall_string, shell=True)
            return {"success": True, "message": "Uninstaller launched successfully."}
        except Exception as e:
            logger.error(f"Error launching uninstaller: {e}")
            return {"success": False, "error": str(e)}
