import os
import shutil
import send2trash
from typing import Callable, Dict, List

class CleanupEngine:
    def __init__(self, config=None):
        self.config = config

    def cleanup(self, files: List[dict], options: dict, progress_cb: Callable = None) -> Dict:
        use_recycle_bin = options.get("recycle_bin", True)
        secure_shred = options.get("secure_shred", False)

        deleted = 0
        failed = 0
        space_freed = 0
        total = len(files)

        for i, f in enumerate(files):
            p = f.get("file_path") or f.get("path")
            size = f.get("size_bytes", 0)
            if not p or not os.path.exists(p):
                continue

            try:
                if secure_shred:
                    self._secure_shred(p)
                elif use_recycle_bin:
                    send2trash.send2trash(p)
                else:
                    if os.path.isdir(p):
                        shutil.rmtree(p)
                    else:
                        os.remove(p)

                deleted += 1
                space_freed += size
            except Exception:
                failed += 1

            if progress_cb and total:
                progress_cb(i + 1, total, f"Cleaning {os.path.basename(p)}")

        return {
            "files_deleted": deleted,
            "files_failed": failed,
            "space_freed_bytes": space_freed,
            "space_freed_gb": space_freed / (1024 ** 3)
        }

    def _secure_shred(self, path: str, passes: int = 1):
        if not os.path.exists(path):
            return
        if os.path.isfile(path):
            size = os.path.getsize(path)
            with open(path, "ba+", buffering=0) as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(size))
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
