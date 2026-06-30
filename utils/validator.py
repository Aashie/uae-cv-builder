import json
from jsonschema import validate, ValidationError
from utils.data_loader import load_json

def validate_profile(profile_data):
    """Checks if profile data matches the master schema."""
    # Note: Ensure data/master_profile_schema.json exists!
    schema = load_json("data/master_profile_schema.json")
    try:
        validate(instance=profile_data, schema=schema)
        print("✅ Profile is valid!")
        return True
    except ValidationError as e:
        print(f"❌ Validation Error: {e.message}")
        return False