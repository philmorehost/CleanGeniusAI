import time
import psutil

class PerformanceMonitor:
    def get_timestamp(self):
        return time.time()

    def get_system_metrics(self):
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        return {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024)
        }
