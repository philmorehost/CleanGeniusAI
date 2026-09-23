import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

from rules.rules_engine import RulesEngine
from recommendation_service import RecommendationService
from software.software_manager import SoftwareManager

class TestHybridRulesAndSoftware(unittest.TestCase):
    def setUp(self):
        self.rules_engine = RulesEngine()
        self.recommendation_service = RecommendationService()
        self.software_manager = SoftwareManager()

    def test_rules_engine_analysis(self):
        scan_results = {
            "categories": {
                "temp_files": {"size_bytes": 2 * 1024**3, "count": 10},
                "dev_cache": {"size_bytes": 5 * 1024**3, "count": 500},
                "system_protected": {"size_bytes": 10 * 1024**3, "count": 1}
            }
        }
        res = self.rules_engine.analyze(scan_results)
        self.assertEqual(res["engine"], "local_rules")
        self.assertFalse(res["ai_enhanced"])

        recs = {r["category"]: r for r in res["recommendations"]}
        self.assertEqual(recs["temp_files"]["action"], "delete")
        self.assertEqual(recs["temp_files"]["safety_score"], 10)
        self.assertEqual(recs["dev_cache"]["action"], "delete")
        self.assertEqual(recs["system_protected"]["action"], "keep")
        self.assertEqual(recs["system_protected"]["safety_score"], 1)

    def test_recommendation_service_local_fallback(self):
        scan_results = {
            "categories": {
                "browser_cache": {"size_bytes": 1 * 1024**3, "count": 100}
            }
        }
        # Calling with ai_enabled=False should return local_rules
        res = self.recommendation_service.analyze(scan_results, ai_enabled=False)
        self.assertEqual(res["engine"], "local_rules")
        self.assertFalse(res["ai_enhanced"])

    def test_software_manager_protected_components(self):
        self.assertTrue(self.software_manager._is_protected("Microsoft Visual C++ 2015-2022 Redistributable"))
        self.assertTrue(self.software_manager._is_protected("DirectX Runtime"))
        self.assertFalse(self.software_manager._is_protected("Obsolete Game Title"))

        apps = self.software_manager.scan_installed_software()
        self.assertIsInstance(apps, list)

if __name__ == "__main__":
    unittest.main()
