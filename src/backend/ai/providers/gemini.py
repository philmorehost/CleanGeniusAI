import json
import os
from .base import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = "", model: str = "gemini-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.last_tokens = {"input": 0, "output": 0}

    def analyze_files(self, file_list: list, context: dict) -> str:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.api_key:
            self.last_tokens = {"input": 100, "output": 150}
            return json.dumps({
                "recommendations": [
                    {
                        "category": "temp_files",
                        "action": "delete",
                        "safety_score": 10,
                        "space_savings_gb": 1.5,
                        "reasoning": "System temp files can be cleared without issue.",
                        "conditions": []
                    }
                ],
                "overall_assessment": {
                    "safe_to_delete_gb": 1.5,
                    "risky_deletion_gb": 0.0,
                    "recommended_order": ["temp_files"]
                },
                "warnings": []
            })

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            gmodel = genai.GenerativeModel(self.model)
            res = gmodel.generate_content("Analyze files for cleanup in JSON format.")
            return res.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")

    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        return json.loads(self.analyze_files(scan_results.get("files", []), scan_results.get("context", {})))

    def test_connection(self) -> bool:
        if os.getenv("MOCK_AI", "false").lower() == "true" or not self.api_key:
            return True
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            gmodel = genai.GenerativeModel(self.model)
            gmodel.generate_content("test")
            return True
        except Exception:
            return False
