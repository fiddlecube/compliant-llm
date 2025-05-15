import json
import os
from pathlib import Path


def save_report(report_data, output_path="reports/report.json"):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the report
    Path(output_path).write_text(json.dumps(report_data, indent=2))