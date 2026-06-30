print("--- Starting test_loader.py ---")
from utils.data_loader import load_profile

try:
    print("Attempting to load profile...")
    profile = load_profile("sample_profile")
    print("Success! Loaded profile.")
    print("Name: " + profile['personal_info']['name'])
    print("Target Role: " + profile['career_identity']['target_roles'][0])
except Exception as e:
    print("Error encountered: " + str(e))