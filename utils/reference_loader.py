"""
Reference Data Loader

Purpose:
Load reference JSON files used by parser and matching modules.
"""

import json
from pathlib import Path


def load_reference_data(filename):
    """Load a JSON reference file from data/reference."""
    reference_path = Path("data") / "reference" / filename

    with open(reference_path, "r", encoding="utf-8") as file:
        return json.load(file)
