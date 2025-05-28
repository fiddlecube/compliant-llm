import os
import uuid

def get_client_id() -> str:
    """Retrieve or create a unique, anonymous client ID for this user."""
    path = os.path.join(os.path.expanduser("~"), ".compliant-llm", ".client-id")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()

    # Generate and save a new UUID
    new_id = str(uuid.uuid4())
    with open(path, "w") as f:
        f.write(new_id)
    return new_id
