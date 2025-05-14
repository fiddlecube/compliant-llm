import json
import os
from pathlib import Path


def save_report(report, out_path="reports/report.json"):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Save the report
    Path(out_path).write_text(json.dumps(report, indent=2))