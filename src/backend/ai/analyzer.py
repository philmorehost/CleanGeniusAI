import os
import time
from .factory import AIProviderFactory
from .optimizer import PromptOptimizer

class AIAnalyzer:
    def __init__(self, config=None):
        self.config = config
        self.current_provider = os.getenv("DEFAULT_AI_PROVIDER", "deepseek")
        self.optimizer = PromptOptimizer()
        self._provider_cache = {}

    def _get_provider(self, name=None, api_key=None):
        pname = (name or self.current_provider).lower()
        if not api_key:
            api_key = os.getenv(f"{pname.upper()}_API_KEY", "")
        else:
            os.environ[f"{pname.upper()}_API_KEY"] = api_key

        if api_key or pname not in self._provider_cache:
            self._provider_cache[pname] = AIProviderFactory.create_provider(pname, api_key)
        return self._provider_cache[pname]

    def analyze(self, scan_results: dict) -> dict:
        compressed = self.optimizer.compress_scan_data(scan_results)
        providers_to_try = [self.current_provider, "gemini", "ollama"]

        for pname in providers_to_try:
            try:
                provider = self._get_provider(pname)
                res = provider.get_cleanup_recommendations(compressed)
                if res and "recommendations" in res:
                    return res
            except Exception:
                continue

        return self.generate_local_recommendations(scan_results)

    def generate_local_recommendations(self, scan_results: dict) -> dict:
        recs = []
        cat_meta = {
            "temp_files": {"action": "delete", "safety_score": 10, "reasoning": "Temporary system and app files are safe to clear."},
            "browser_cache": {"action": "delete", "safety_score": 9, "reasoning": "Browser web caches consume space without affecting user data."},
            "dev_cache": {"action": "delete", "safety_score": 9, "reasoning": "Build artifacts (node_modules, __pycache__, dist, .next) can be safely regenerated."},
            "log_files": {"action": "delete", "safety_score": 8, "reasoning": "Diagnostic and application log files."},
            "installers": {"action": "review", "safety_score": 7, "reasoning": "Downloaded setup packages and installer archives."},
            "registry_junk": {"action": "delete", "safety_score": 9, "reasoning": "Invalid MRU keys, uninstaller entries, and orphaned DLL paths."},
            "duplicate_files": {"action": "review", "safety_score": 8, "reasoning": "Duplicate files consuming redundant disk space."},
            "miscellaneous": {"action": "review", "safety_score": 6, "reasoning": "Uncategorized leftover files."}
        }

        categories = scan_results.get("categories", {})
        total_safe_bytes = 0
        order = []

        for cat, data in categories.items():
            meta = cat_meta.get(cat, {"action": "review", "safety_score": 6, "reasoning": f"Scanned {cat} files."})
            size_gb = round((data.get("size_bytes", 0)) / (1024**3), 2)
            recs.append({
                "category": cat,
                "action": meta["action"],
                "safety_score": meta["safety_score"],
                "space_savings_gb": size_gb,
                "reasoning": meta["reasoning"],
                "conditions": []
            })
            if meta["safety_score"] >= 8:
                total_safe_bytes += data.get("size_bytes", 0)
                order.append(cat)

        return {
            "recommendations": recs,
            "overall_assessment": {
                "safe_to_delete_gb": round(total_safe_bytes / (1024**3), 2),
                "risky_deletion_gb": 0.0,
                "recommended_order": order
            },
            "warnings": ["Operating in local autonomous mode."]
        }

    def get_token_count(self):
        p = self._get_provider(self.current_provider)
        return getattr(p, "last_tokens", {"input": 0, "output": 0})

    def test_provider(self, provider_name: str, api_key: str = None) -> dict:
        t0 = time.time()
        try:
            p = self._get_provider(provider_name, api_key=api_key)
            success, msg = p.test_connection_detailed()
            return {
                "success": success,
                "response_time": round(time.time() - t0, 3),
                "message": msg
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": round(time.time() - t0, 3),
                "message": str(e)
            }

    def get_available_providers(self):
        return [
            {"id": "deepseek", "name": "DeepSeek", "type": "free_paid", "cost": "$0.14/1M tokens"},
            {"id": "openai", "name": "OpenAI", "type": "paid", "cost": "$0.50/1M tokens"},
            {"id": "claude", "name": "Claude", "type": "paid", "cost": "$3.00/1M tokens"},
            {"id": "gemini", "name": "Google Gemini", "type": "free", "cost": "Free tier available"},
            {"id": "ollama", "name": "Ollama (Local)", "type": "local", "cost": "Free (Runs locally)"}
        ]
