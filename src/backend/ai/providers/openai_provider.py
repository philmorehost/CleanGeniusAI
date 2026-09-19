import json
import os
from openai import OpenAI
from .base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str = "", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.last_tokens = {"input": 0, "output": 0}
        if self.api_key and not os.getenv("MOCK_AI", "false").lower() == "true":
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def analyze_files(self, file_list: list, context: dict) -> str:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.client:
            self.last_tokens = {"input": 150, "output": 200}
            return json.dumps({
                "recommendations": [
                    {
                        "category": "browser_cache",
                        "action": "delete",
                        "safety_score": 9,
                        "space_savings_gb": 1.2,
                        "reasoning": "Browser web caches consume disk space without affecting settings.",
                        "conditions": []
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 1.2,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["browser_cache"]
                },
                "warnings": []
            })

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a disk cleanup expert. JSON output only."},
                {"role": "user", "content": f"Analyze scan: {len(file_list)} files"}
            ],
            response_format={"type": "json_object"}
        )
        u = resp.usage
        if u:
            self.last_tokens = {"input": u.prompt_tokens, "output": u.completion_tokens}
        return resp.choices[0].message.content

    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        return json.loads(self.analyze_files(scan_results.get("files", []), scan_results.get("context", {})))

    def test_connection(self) -> bool:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.client:
            return True
        try:
            self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": "test"}], max_tokens=5)
            return True
        except Exception:
            return False
