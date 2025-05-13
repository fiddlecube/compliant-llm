import json
from pathlib import Path

def save_report(report, out_path="report.json"):
    Path(out_path).write_text(json.dumps(report, indent=2))