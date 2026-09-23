import csv
import json
from pathlib import Path

class ReportGenerator:
    def generate_json(self, data: dict, file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_csv(self, data: dict, file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        files = data.get("files") or data.get("recommendations") or []
        if not files:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("No data available\n")
            return

        keys = list(files[0].keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(files)

    def generate_pdf(self, data: dict, file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "CleanGenius AI - Cleanup Report", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.set_font("Helvetica", "", 12)
            pdf.ln(10)

            for k, v in data.items():
                if isinstance(v, (str, int, float, bool)):
                    pdf.cell(0, 8, f"{k}: {v}", new_x="LMARGIN", new_y="NEXT")
            pdf.output(file_path)
        except Exception:
            # Fallback to plain text JSON format if PDF generation fails
            self.generate_json(data, file_path)
