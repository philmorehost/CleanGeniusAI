import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/backend')))

from database.models import Database
from scanner.disk_scanner import DiskScanner
from ai.analyzer import AIAnalyzer
from cleanup.cleanup_engine import CleanupEngine
from cleanup.safety_manager import SafetyManager

def test_database_initialization(tmp_path):
    db_file = tmp_path / "test.db"
    db = Database(str(db_file))
    sid = db.create_scan_session("fast")
    assert sid > 0

    session = db.get_scan_session(sid)
    assert session["scan_type"] == "fast"
    assert session["status"] == "running"

def test_disk_scanner(tmp_path):
    # Create test directory structure
    d = tmp_path / "test_dir"
    d.mkdir()
    f1 = d / "test.tmp"
    f1.write_text("dummy temp content")

    scanner = DiskScanner()
    res = scanner.scan("custom", paths=[str(d)])

    assert res["total_files"] == 1
    assert res["files"][0]["category"] == "temp_files"

def test_ai_analyzer_fallback(monkeypatch):
    monkeypatch.setenv("MOCK_AI", "true")
    analyzer = AIAnalyzer()
    res = analyzer.analyze({"files": [], "context": {}})
    assert "recommendations" in res
    assert len(res["recommendations"]) > 0

def test_safety_manager_and_cleanup(tmp_path):
    d = tmp_path / "cleanup_dir"
    d.mkdir()
    f = d / "file_to_delete.tmp"
    f.write_text("delete me")

    sm = SafetyManager()
    file_info = [{"path": str(f), "size_bytes": 10}]
    check = sm.check_files(file_info)
    assert check["safe"] is True

    engine = CleanupEngine()
    res = engine.cleanup(file_info, {"recycle_bin": False})
    assert res["files_deleted"] == 1
    assert not f.exists()
