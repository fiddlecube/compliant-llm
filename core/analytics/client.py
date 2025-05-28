from pathlib import Path
import uuid

def get_client_id() -> str:
    """Retrieve or create a unique, anonymous client ID for this user."""
    user_home = Path.home()
    client_id_path = user_home / ".compliant-llm" / ".client-id"
    client_id_path.parent.mkdir(parents=True, exist_ok=True)

    if client_id_path.exists():
        with open(client_id_path, "r") as f:
            return f.read().strip()

    # Generate and save a new UUID
    new_id = str(uuid.uuid4())
    with open(client_id_path, "w") as f:
        f.write(new_id)
    return new_id
