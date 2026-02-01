"""
Seeds initial dummy data for development/testing.
"""

import json
from pathlib import Path

DATA_FILE = Path("data/sample.json")

def seed():
    data = {
        "users": [
            {"id": 1, "name": "Test User"}
        ]
    }

    DATA_FILE.parent.mkdir(exist_ok=True)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("[OK] Sample data seeded")

if __name__ == "__main__":
    seed()
