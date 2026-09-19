from abc import ABC, abstractmethod
from typing import Dict, List

class AIProvider(ABC):
    @abstractmethod
    def analyze_files(self, file_list: List[dict], context: dict) -> str:
        pass

    @abstractmethod
    def get_cleanup_recommendations(self, scan_results: dict) -> dict:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass
