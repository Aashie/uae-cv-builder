from utils.data_loader import load_profile
from utils.validator import validate_profile

# Load your profile
profile = load_profile("sample_profile")

# Run the validation check
validate_profile(profile)