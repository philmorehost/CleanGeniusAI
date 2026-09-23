import os
import sys
import psutil
import platform
import logging
from threading import Thread
import signal
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.logger import setup_logger
from utils.config import Config
from database.models import Database
from scanner.disk_scanner import DiskScanner
from scanner.duplicate_finder import DuplicateFinder
from scanner.registry_scanner import RegistryScanner
from ai.analyzer import AIAnalyzer
from cleanup.cleanup_engine import CleanupEngine
from cleanup.safety_manager import SafetyManager
from cleanup.rollback import RollbackManager
from monitoring.performance import PerformanceMonitor
from monitoring.cost_tracker import CostTracker
from security.encryption import SecureStorage
from reports.generator import ReportGenerator

app = Flask(__name__)
CORS(app)

logger = setup_logger("cleangenius", "logs/app.log")
config = Config()
db = Database()
scanner = DiskScanner(config)
duplicate_finder = DuplicateFinder()
registry_scanner = RegistryScanner()
ai_analyzer = AIAnalyzer(config)
cleanup_engine = CleanupEngine(config)
safety_manager = SafetyManager(config)
rollback_manager = RollbackManager(db)
performance_monitor = PerformanceMonitor()
cost_tracker = CostTracker(db)
secure_storage = SecureStorage()
report_generator = ReportGenerator()

active_scans = {}
active_cleanups = {}

@app.route("/api/system/info", methods=["GET"])
def get_system_info():
    try:
        root_path = "C:\\" if platform.system() == "Windows" else "/"
        usage = psutil.disk_usage(root_path)

        drives = []
        for partition in psutil.disk_partitions():
            try:
                pu = psutil.disk_usage(partition.mountpoint)
                drives.append({
                    "drive": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(pu.total / (1024**3), 2),
                    "used_gb": round(pu.used / (1024**3), 2),
                    "free_gb": round(pu.free / (1024**3), 2),
                    "percent": pu.percent
                })
            except Exception:
                pass

        return jsonify({
            "success": True,
            "data": {
                "os": platform.system(),
                "os_version": platform.version(),
                "processor": platform.processor(),
                "total_space_gb": round(usage.total / (1024**3), 2),
                "used_space_gb": round(usage.used / (1024**3), 2),
                "free_space_gb": round(usage.free / (1024**3), 2),
                "percent_used": usage.percent,
                "drives": drives
            }
        })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/scan/start", methods=["POST"])
def start_scan():
    try:
        data = request.json or {}
        scan_mode = data.get("mode", "fast")
        paths = data.get("paths", [])
        options = data.get("options", {})

        scan_id = db.create_scan_session(scan_mode)

        def worker():
            try:
                def update_cb(current, total, msg=""):
                    p = int((current / total) * 100) if total > 0 else 0
                    if scan_id in active_scans:
                        active_scans[scan_id]["progress"] = p
                        active_scans[scan_id]["message"] = msg or f"Scanning files ({p}%)..."
                    db.update_scan_progress(scan_id, p, msg or f"Scanning files ({p}%)...")

                update_cb(1, 100, "Starting file scan engine...")

                if scan_mode == "registry":
                    res = registry_scanner.scan(update_cb)
                else:
                    res = scanner.scan(scan_mode, paths, options, update_cb)

                if options.get("find_duplicates", True) and res.get("files"):
                    update_cb(80, 100, "Analyzing duplicate files...")
                    dupes = duplicate_finder.find_duplicates(res["files"], update_cb)
                    res["duplicates"] = dupes

                db.store_scan_results(scan_id, res)

                if options.get("ai_analysis", True):
                    update_cb(90, 100, "Generating AI recommendations...")
                    try:
                        ai_recs = ai_analyzer.analyze(res)
                        db.store_ai_recommendations(scan_id, ai_recs)
                        res["ai_recommendations"] = ai_recs
                    except Exception as ai_err:
                        logger.error(f"AI analysis non-fatal error: {ai_err}")

                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "completed"
                    active_scans[scan_id]["progress"] = 100
                    active_scans[scan_id]["message"] = "Scan completed successfully."
                    active_scans[scan_id]["results"] = res
                db.complete_scan_session(scan_id, res)
            except Exception as ex:
                logger.error(f"Scan error in worker: {ex}")
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "failed"
                    active_scans[scan_id]["error"] = str(ex)
                    active_scans[scan_id]["message"] = f"Scan failed: {ex}"
                db.fail_scan_session(scan_id, str(ex))

        thread = Thread(target=worker)
        thread.daemon = True

        active_scans[scan_id] = {
            "thread": thread,
            "status": "running",
            "progress": 1,
            "message": "Initializing scan session..."
        }

        thread.start()

        return jsonify({
            "success": True,
            "scan_id": scan_id,
            "message": "Scan started"
        })
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/scan/<int:scan_id>", methods=["GET"])
def get_scan_status(scan_id):
    try:
        if scan_id in active_scans:
            sc = active_scans[scan_id]
            return jsonify({
                "success": True,
                "status": sc["status"],
                "progress": sc.get("progress", 0),
                "message": sc.get("message", ""),
                "error": sc.get("error", None),
                "results": sc.get("results") if sc["status"] == "completed" else None
            })

        session = db.get_scan_session(scan_id)
        if session:
            return jsonify({
                "success": True,
                "status": session.get("status", "completed"),
                "results": session
            })

        return jsonify({"success": False, "error": "Scan session not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/cleanup/start", methods=["POST"])
def start_cleanup():
    try:
        data = request.json or {}
        scan_id = data.get("scan_id")
        categories = data.get("categories", [])
        file_ids = data.get("file_ids", [])
        options = data.get("options", {})

        files = db.get_files_for_cleanup(scan_id, categories, file_ids)
        safety = safety_manager.check_files(files)

        strict_safety = options.get("strict_safety", False)
        if not safety["safe"] and strict_safety:
            return jsonify({
                "success": False,
                "error": "Safety check blocked deletion of protected or open files.",
                "details": safety
            }), 400

        # Filter to safe files unless strict_safety was enforced
        files_to_clean = safety.get("safe_files", files) if not safety["safe"] else files

        cleanup_id = db.create_cleanup_session(scan_id)

        def worker():
            try:
                def update_cb(curr, total, msg=""):
                    p = int((curr / total) * 100) if total > 0 else 0
                    if cleanup_id in active_cleanups:
                        active_cleanups[cleanup_id]["progress"] = p
                        active_cleanups[cleanup_id]["message"] = msg or f"Cleaning files ({p}%)..."
                    db.update_cleanup_progress(cleanup_id, p, msg or f"Cleaning files ({p}%)...")

                update_cb(1, 100, "Creating rollback point...")

                if config.get("safety.enable_rollback", True):
                    rollback_manager.create_restore_point(cleanup_id, files_to_clean)

                res = cleanup_engine.cleanup(files_to_clean, options, update_cb)
                if cleanup_id in active_cleanups:
                    active_cleanups[cleanup_id]["status"] = "completed"
                    active_cleanups[cleanup_id]["progress"] = 100
                    active_cleanups[cleanup_id]["message"] = "Cleanup completed successfully."
                    active_cleanups[cleanup_id]["result"] = res
                db.complete_cleanup_session(cleanup_id, res)
            except Exception as ex:
                if cleanup_id in active_cleanups:
                    active_cleanups[cleanup_id]["status"] = "failed"
                    active_cleanups[cleanup_id]["error"] = str(ex)
                    active_cleanups[cleanup_id]["message"] = f"Cleanup failed: {ex}"
                db.fail_cleanup_session(cleanup_id, str(ex))

        thread = Thread(target=worker)
        thread.daemon = True

        active_cleanups[cleanup_id] = {
            "thread": thread,
            "status": "running",
            "progress": 1,
            "message": "Initializing cleanup session..."
        }

        thread.start()

        return jsonify({"success": True, "cleanup_id": cleanup_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/cleanup/<int:cleanup_id>", methods=["GET"])
def get_cleanup_status(cleanup_id):
    try:
        if cleanup_id in active_cleanups:
            cl = active_cleanups[cleanup_id]
            return jsonify({
                "success": True,
                "status": cl["status"],
                "progress": cl.get("progress", 0),
                "message": cl.get("message", ""),
                "error": cl.get("error", None),
                "result": cl.get("result") if cl["status"] == "completed" else None
            })

        session = db.get_cleanup_session(cleanup_id)
        if session:
            return jsonify({"success": True, "status": "completed", "result": session})

        return jsonify({"success": False, "error": "Cleanup session not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/cleanup/rollback/<int:cleanup_id>", methods=["POST"])
def rollback_cleanup(cleanup_id):
    try:
        res = rollback_manager.rollback(cleanup_id)
        if res.get("success"):
            db.mark_cleanup_rolled_back(cleanup_id)
            return jsonify({"success": True, "message": f"Restored {res.get('files_restored', 0)} files"})
        return jsonify({"success": False, "error": "Rollback failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/analyze", methods=["POST"])
def ai_analyze():
    try:
        data = request.json or {}
        recs = ai_analyzer.analyze(data)
        tokens = ai_analyzer.get_token_count()

        cost = cost_tracker.log_usage(
            provider=ai_analyzer.current_provider,
            model="default",
            input_tokens=tokens.get("input", 0),
            output_tokens=tokens.get("output", 0)
        )
        recs["cost_usd"] = cost
        return jsonify({"success": True, "recommendations": recs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/settings", methods=["POST"])
def update_ai_settings():
    try:
        data = request.json or {}
        provider = data.get("provider", "deepseek").lower()
        api_key = data.get("api_key", "")
        keys = data.get("keys", {})

        if provider:
            ai_analyzer.current_provider = provider
            os.environ["DEFAULT_AI_PROVIDER"] = provider

        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key

        for p_name, p_key in keys.items():
            if p_key:
                os.environ[f"{p_name.upper()}_API_KEY"] = p_key

        ai_analyzer._provider_cache.clear()
        return jsonify({"success": True, "message": "AI settings updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/test/<provider>", methods=["GET", "POST"])
def test_ai_provider(provider):
    try:
        data = request.json if request.is_json else {}
        api_key = data.get("api_key") or request.args.get("api_key")
        res = ai_analyzer.test_provider(provider, api_key=api_key)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/providers", methods=["GET"])
def get_ai_providers():
    try:
        return jsonify({"success": True, "providers": ai_analyzer.get_available_providers()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/cost", methods=["GET"])
def get_ai_cost():
    try:
        month = request.args.get("month")
        stats = cost_tracker.get_monthly_stats(month)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/export", methods=["POST"])
def export_report():
    try:
        data = request.json or {}
        rtype = data.get("type", "pdf")
        fpath = data.get("filePath", "report.pdf")
        rdata = data.get("data", {})

        if rtype == "pdf":
            report_generator.generate_pdf(rdata, fpath)
        elif rtype == "csv":
            report_generator.generate_csv(rdata, fpath)
        else:
            report_generator.generate_json(rdata, fpath)

        return jsonify({"success": True, "message": f"Report exported to {fpath}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        latest = db.get_latest_scan()
        sys_info = get_system_info().json.get("data", {})
        activity = db.get_recent_activity(10)
        ai_cost = cost_tracker.get_monthly_stats()

        score = 100
        if sys_info.get("percent_used", 0) > 85:
            score -= 25
        elif sys_info.get("percent_used", 0) > 70:
            score -= 10

        if latest:
            junk_gb = latest.get("total_size_bytes", 0) / (1024**3)
            if junk_gb > 30:
                score -= 25
            elif junk_gb > 10:
                score -= 10

        return jsonify({
            "success": True,
            "data": {
                "health_score": max(0, score),
                "system_info": sys_info,
                "latest_scan": latest,
                "recent_activity": activity,
                "ai_cost": ai_cost
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": performance_monitor.get_timestamp()
    })

if __name__ == "__main__":
    logger.info("Starting CleanGenius AI Python Backend on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
