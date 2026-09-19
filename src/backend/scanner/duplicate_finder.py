import hashlib
import os
from collections import defaultdict
from typing import Callable, Dict, List, Optional

class DuplicateFinder:
    CHUNK = 1024 * 1024

    def _hash_file(self, path: str) -> Optional[str]:
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(self.CHUNK)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except (OSError, PermissionError):
            return None

    def find_duplicates(self, files: List[dict], progress_cb: Optional[Callable] = None) -> Dict:
        by_size = defaultdict(list)
        for f in files:
            size = f.get("size_bytes", 0)
            if size < 512:  # skip tiny files
                continue
            by_size[size].append(f)

        groups = []
        wasted = 0
        candidates = [g for g in by_size.values() if len(g) > 1]
        total = len(candidates)

        for i, group in enumerate(candidates):
            hashes = defaultdict(list)
            for f in group:
                path = f.get("path") or f.get("file_path")
                digest = self._hash_file(path)
                if digest:
                    hashes[digest].append(f)
            for digest, items in hashes.items():
                if len(items) > 1:
                    items.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
                    extra = items[1:]
                    wasted += sum(x.get("size_bytes", 0) for x in extra)
                    groups.append({
                        "hash": digest,
                        "keep": items[0],
                        "duplicates": extra,
                        "count": len(items),
                        "wasted_bytes": sum(x.get("size_bytes", 0) for x in extra),
                    })
            if progress_cb and total:
                progress_cb(i + 1, total, "Finding duplicates...")

        return {
            "groups": groups,
            "duplicate_count": sum(g["count"] - 1 for g in groups),
            "wasted_bytes": wasted,
            "wasted_gb": wasted / (1024 ** 3),
        }
