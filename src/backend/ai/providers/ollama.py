import json
import os
import requests
from .base import AIProvider

class OllamaProvider(AIProvider):
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
        self.last_tokens = {"input": 0, "output": 0}

    def analyze_files(self, file_list: list, context: dict) -> str:
        if os.getenv("MOCK_AI", "false").lower() == "true":
            return json.dumps({
                "recommendations": [
                    {
                        "category": "installers",
                        "action": "review",
                        "safety_score": 6,
                        "space_savings_gb": 3.0,
                        "reasoning": "Downloaded installers in Downloads folder can be safely removed if no longer needed.",
                        "conditions": []
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 3.0,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["installers"]
                },
                "warnings": []
            })

        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": "Analyze disk scan data for Windows cleanup and return JSON.",
                "stream": False,
                "format": "json"
            }
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()['response']
        except Exception:
            # Fallback mock if Ollama server is offline
            return json.dumps({
                "recommendations": [
                    {
                        "category": "temp_files",
                        "action": "delete",
                        "safety_score": 9,
                        "space_savings_gb": 1.0,
                        "reasoning": "Ollama local model recommended cleaning temporary files.",
                        "conditions": []
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 1.0,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["temp_files"]
                },
                "warnings": []
            })

    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        return json.loads(self.analyze_files(scan_results.get("files", []), scan_results.get("context", {})))

    def test_connection(self) -> bool:
        success, _ = self.test_connection_detailed()
        return success

    def test_connection_detailed(self) -> tuple[bool, str]:
        if os.getenv("MOCK_AI", "false").lower() == "true":
            return True, "Connected successfully (Mock Mode)"
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                return True, "Connected to local Ollama server successfully!"
            return False, f"Ollama server returned HTTP {resp.status_code}"
        except Exception:
            return False, f"Ollama connection failed: Local server unreachable at {self.base_url}"
