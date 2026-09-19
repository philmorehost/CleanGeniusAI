class PromptOptimizer:
    @staticmethod
    def compress_scan_data(scan_results: dict) -> dict:
        files = scan_results.get("files", [])
        categories = {}
        for f in files[:100]:
            cat = f.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"count": 0, "size_bytes": 0, "samples": []}
            categories[cat]["count"] += 1
            categories[cat]["size_bytes"] += f.get("size_bytes", 0)
            if len(categories[cat]["samples"]) < 3:
                categories[cat]["samples"].append(f.get("path") or f.get("file_path", ""))

        return {
            "files": files[:100],
            "summary": categories,
            "total_files": len(files),
            "context": scan_results.get("context", {})
        }
