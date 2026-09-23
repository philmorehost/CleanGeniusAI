import json
import os
import time
from typing import Dict, List
from openai import OpenAI
from .base import AIProvider

class DeepSeekProvider(AIProvider):
    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.last_tokens = {"input": 0, "output": 0}

        if self.api_key and not os.getenv("MOCK_AI", "false").lower() == "true":
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    def _build_prompt(self, file_list: List[dict], context: dict) -> str:
        cats = {}
        for f in file_list[:200]:
            c = f.get("category", "unknown")
            cats.setdefault(c, {"count": 0, "size": 0})
            cats[c]["count"] += 1
            cats[c]["size"] += f.get("size_bytes", 0)

        summary = "\n".join(
            f"- {k}: {v['count']} files, {v['size']/(1024**3):.2f} GB" for k, v in cats.items()
        )
        return f"""You are an expert Windows disk cleanup assistant. Analyze disk scan data and provide recommendations.
Context: {json.dumps(context)}
Categories detected:
{summary}

Return valid JSON in this structure:
{{
  "recommendations": [
    {{
      "category": "category_name",
      "action": "delete|keep|review",
      "safety_score": 9,
      "space_savings_gb": 1.5,
      "reasoning": "Reason for recommendation",
      "conditions": []
    }}
  ],
  "overall_assessment": {{
    "safe_to_delete_gb": 1.5,
    "risky_deletion_gb": 0.2,
    "recommended_order": ["temp_files", "browser_cache"]
  }},
  "warnings": []
}}"""

    def analyze_files(self, file_list: List[dict], context: dict) -> str:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.client:
            self.last_tokens = {"input": 120, "output": 250}
            return json.dumps({
                "recommendations": [
                    {
                        "category": "temp_files",
                        "action": "delete",
                        "safety_score": 10,
                        "space_savings_gb": 2.4,
                        "reasoning": "Temporary system and app files are safe to delete.",
                        "conditions": []
                    },
                    {
                        "category": "dev_cache",
                        "action": "delete",
                        "safety_score": 9,
                        "space_savings_gb": 5.1,
                        "reasoning": "Build artifacts (node_modules, __pycache__) can be safely regenerated.",
                        "conditions": ["Re-run npm install or build commands if needed"]
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 7.5,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["temp_files", "dev_cache"]
                },
                "warnings": []
            })

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a disk cleanup expert. JSON output only."},
                {"role": "user", "content": self._build_prompt(file_list, context)}
            ],
            temperature=0.2,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        u = resp.usage
        if u:
            self.last_tokens = {"input": u.prompt_tokens, "output": u.completion_tokens}
        return resp.choices[0].message.content

    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        raw = self.analyze_files(scan_results.get("files", []), scan_results.get("context", {}))
        return json.loads(raw)

    def _ensure_client(self):
        if not self.api_key:
            self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if self.api_key and not self.client and not os.getenv("MOCK_AI", "false").lower() == "true":
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def test_connection(self) -> bool:
        success, _ = self.test_connection_detailed()
        return success

    def test_connection_detailed(self) -> tuple[bool, str]:
        if os.getenv("MOCK_AI", "false").lower() == "true":
            return True, "Connected successfully (Mock Mode)"
        self._ensure_client()
        if not self.api_key or not self.client:
            return False, "DeepSeek API key is missing. Please enter your API key."
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            return True, "Connected to DeepSeek API successfully!"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "auth" in err_str.lower() or "invalid" in err_str.lower():
                return False, "Authentication failed: Invalid DeepSeek API Key."
            if "429" in err_str or "quota" in err_str.lower():
                return False, "Rate limit or quota exceeded on DeepSeek account."
            return False, f"DeepSeek API error: {err_str}"
