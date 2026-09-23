import os
import platform

def is_windows():
    return platform.system() == "Windows" and os.getenv("MOCK_WINDOWS", "false").lower() != "true"

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"
