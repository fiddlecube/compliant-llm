import json
import os
from pathlib import Path
from datetime import datetime



def save_report(report_data, output_path):
    # Create directories if they don't exist
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{output_path['path']}/{output_path['filename']}_{timestamp}.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    report_metadata = {
        "path": file_path,
        "created_at": timestamp
    }
    report_data['report_metadata'] = report_metadata
    # Save the report
    Path(file_path).write_text(json.dumps(report_data, indent=2))
    return file_path
