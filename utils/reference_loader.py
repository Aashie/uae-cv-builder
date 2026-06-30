import json
import os

def load_reference_data(filename):
    """
    Purpose: Reads JSON from data/reference/ and returns the content.
    Inputs: Name of the file (e.g., 'skills.json').
    Outputs: Dictionary or list from the JSON file.
    """
    # Navigate to the root directory from /utils/
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, 'data', 'reference', filename)
    
    with open(file_path, 'r') as f:
        return json.load(f)
