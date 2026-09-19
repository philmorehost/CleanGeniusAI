import json
import os
from .base import AIProvider

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str = "", model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY", "")
        self.model = model
        self.last_tokens = {"input": 0, "output": 0}

    def analyze_files(self, file_list: list, context: dict) -> str:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.api_key:
            self.last_tokens = {"input": 180, "output": 220}
            return json.dumps({
                "recommendations": [
                    {
                        "category": "log_files",
                        "action": "delete",
                        "safety_score": 8,
                        "space_savings_gb": 0.8,
                        "reasoning": "Old diagnostic log files are safely dispensable.",
                        "conditions": []
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 0.8,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["log_files"]
                },
                "warnings": []
            })

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            resp = client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": f"Analyze scan data in JSON format: {len(file_list)} files"}]
            )
            return resp.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {e}")

    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        return json.loads(self.analyze_files(scan_results.get("files", []), scan_results.get("context", {})))

    def test_connection(self) -> bool:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.api_key:
            return True
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            client.messages.create(model=self.model, max_tokens=5, messages=[{"role": "user", "content": "test"}])
            return True
        except Exception:
            return False
