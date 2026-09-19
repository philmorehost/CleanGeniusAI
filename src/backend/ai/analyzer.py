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

    def _get_provider(self, name=None):
        pname = (name or self.current_provider).lower()
        api_key = os.getenv(f"{pname.upper()}_API_KEY", "")
        if pname not in self._provider_cache:
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

        # Fallback rule-based recommendation if AI fails/unavailable
        return {
            "recommendations": [
                {
                    "category": "temp_files",
                    "action": "delete",
                    "safety_score": 10,
                    "space_savings_gb": round(scan_results.get("total_size_gb", 1.0) * 0.4, 2),
                    "reasoning": "Rule-based fallback: Temporary files are safe to remove.",
                    "conditions": []
                },
                {
                    "category": "browser_cache",
                    "action": "delete",
                    "safety_score": 9,
                    "space_savings_gb": round(scan_results.get("total_size_gb", 1.0) * 0.3, 2),
                    "reasoning": "Rule-based fallback: Browser cache can be safely cleared.",
                    "conditions": []
                }
            ],
            "overall_assessment": {
                "safe_to_delete_gb": round(scan_results.get("total_size_gb", 1.0) * 0.7, 2),
                "risky_deletion_gb": 0.0,
                "recommended_order": ["temp_files", "browser_cache"]
            },
            "warnings": ["AI offline - used rule-based recommendations."]
        }

    def get_token_count(self):
        p = self._get_provider(self.current_provider)
        return getattr(p, "last_tokens", {"input": 0, "output": 0})

    def test_provider(self, provider_name: str) -> dict:
        t0 = time.time()
        try:
            p = self._get_provider(provider_name)
            success = p.test_connection()
            return {
                "success": success,
                "response_time": round(time.time() - t0, 3),
                "message": "Connected successfully" if success else "Connection test failed"
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
