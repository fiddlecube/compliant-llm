from pathlib import Path
from tinydb import TinyDB, Query
from typing import List, Dict, Any, Optional
import uuid

DB_DIR = Path.home() / ".compliant-llm"
CONFIG_DB_FILE = DB_DIR / "model_config.json"

# Ensure the .compliant-llm directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

_db_instance = None

def _get_table():
    global _db_instance
    if _db_instance is None:
        _db_instance = TinyDB(CONFIG_DB_FILE)
    return _db_instance.table('model_config')

def save_config(runner_config_data: Dict[str, Any], profile_name: str | None = None) -> None:
    """Saves or updates a model configuration profile."""
    table = _get_table()

    # Ensure 'id' exists, add if not
    if 'id' not in runner_config_data:
        runner_config_data['id'] = str(uuid.uuid4())

    # Ensure 'past_runs' exists if it's a new config or not present
    if 'past_runs' not in runner_config_data:
        runner_config_data['past_runs'] = []
    
    # Add/update profile_name within the document for easier access if needed
    if profile_name is not None:
        runner_config_data['profile_name'] = profile_name
    document_to_store = runner_config_data
    
    ConfigQuery = Query()
    table.upsert(document_to_store, ConfigQuery.id == runner_config_data['id'])
    print(f"Config '{profile_name}' saved.")

def get_config(id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific model configuration profile."""
    table = _get_table()
    ConfigQuery = Query()
    return table.get(ConfigQuery.id == id)

def list_configs() -> List[Dict[str, Any]]:
    """Lists all saved model configuration profiles."""
    table = _get_table()
    return table.all()

def delete_config(id: str) -> bool:
    """Deletes a model configuration profile. Returns True if deleted."""
    table = _get_table()
    ConfigQuery = Query()
    deleted_ids = table.remove(ConfigQuery.id == id)
    return len(deleted_ids) > 0

def add_report_to_config(id: str, report_file_path: str) -> bool:
    """Adds a report file path to the 'past_runs' list of a specific config."""
    table = _get_table()
    ConfigQuery = Query()
    config_doc = table.get(ConfigQuery.id == id)

    if not config_doc:
        print(f"Error: Config profile '{id}' not found.")
        return False

    # Ensure past_runs is a list
    if 'past_runs' not in config_doc or not isinstance(config_doc['past_runs'], list):
        config_doc['past_runs'] = []
    
    # Avoid duplicate entries
    if report_file_path not in config_doc['past_runs']:
        config_doc['past_runs'].append(report_file_path)
        table.upsert(config_doc, ConfigQuery.id == id)
        print(f"Report '{report_file_path}' added to config '{id}'.")
        return True
    else:
        print(f"Report '{report_file_path}' already exists in config '{id}'.")
        return False

def close_db():
    """Closes the database connection."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
