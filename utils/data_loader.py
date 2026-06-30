import json
import os

def load_json(file_path):
    """Helper to load any JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_profile(profile_name):
    """Loads a specific profile by name."""
    path = os.path.join("data", "profiles", f"{profile_name}.json")
    return load_json(path)