"""
CleanGenius AI - Unified Recommendation Service
Combines Local Rules Engine with optional AI Providers.
"""

import logging
from typing import Dict, Any
from rules.rules_engine import RulesEngine
from ai.analyzer import AIAnalyzer

logger = logging.getLogger("cleangenius.recommendation")

class RecommendationService:
    """
    Hybrid Recommendation Service implementing the Strategy pattern.
    - Always executes Local Rules Engine first for instant, guaranteed offline results.
    - If AI enhancement is enabled AND reachable, enhances local recommendations.
    - Applies a local safety floor so AI can never lower safety scores below local safety rules.
    - Silently falls back to local rules if AI fails for any reason (no network, bad key, rate limit).
    """

    def __init__(self, config=None):
        self.config = config
        self.local_engine = RulesEngine()
        self.ai_analyzer = AIAnalyzer(config) if config else None

    def analyze(self, scan_results: Dict[str, Any], ai_enabled: bool = False) -> Dict[str, Any]:
        # 1. ALWAYS run local rules first (instant, 100% reliable)
        local_result = self.local_engine.analyze(scan_results)

        if not ai_enabled or not self.ai_analyzer:
            return local_result

        # 2. If AI enabled, attempt AI enhancement with graceful silent fallback
        try:
            ai_result = self.ai_analyzer.analyze(scan_results)
            if ai_result and isinstance(ai_result, dict) and "recommendations" in ai_result:
                merged = self._merge_results(local_result, ai_result)
                merged["engine"] = "local_rules+ai"
                merged["ai_enhanced"] = True
                return merged
        except Exception as e:
            logger.warning(f"AI enhancement unavailable, falling back to local rules: {e}")

        return local_result

    def _merge_results(self, local: Dict[str, Any], ai: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge AI recommendations into local rules result while enforcing
        the local safety floor.
        """
        local_recs_map = {r["category"]: r for r in local.get("recommendations", [])}
        ai_recs = ai.get("recommendations", [])

        merged_recs = []
        for ai_rec in ai_recs:
            cat = ai_rec.get("category")
            if cat in local_recs_map:
                loc_rec = local_recs_map[cat]
                # Local safety floor enforcement: AI score cannot be lower than local safety floor
                safe_score = max(ai_rec.get("safety_score", 5), loc_rec["safety_score"])
                merged_recs.append({
                    "category": cat,
                    "action": ai_rec.get("action", loc_rec["action"]),
                    "safety_score": safe_score,
                    "space_savings_gb": loc_rec["space_savings_gb"],
                    "reasoning": ai_rec.get("reasoning", loc_rec["reasoning"]),
                    "conditions": loc_rec["conditions"] + ["🤖 AI-Enhanced Reasoning"]
                })
            else:
                merged_recs.append(ai_rec)

        # Include any local category not mentioned by AI
        ai_cat_set = {r.get("category") for r in ai_recs}
        for cat, loc_rec in local_recs_map.items():
            if cat not in ai_cat_set:
                merged_recs.append(loc_rec)

        return {
            "engine": "local_rules+ai",
            "ai_enhanced": True,
            "recommendations": merged_recs,
            "overall_assessment": ai.get("overall_assessment", local.get("overall_assessment", {})),
            "warnings": local.get("warnings", []) + ai.get("warnings", [])
        }
