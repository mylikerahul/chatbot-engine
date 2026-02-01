"""
Initial project setup script.
Creates required folders and checks environment readiness.
"""

import os

FOLDERS = ["logs", "data"]

def setup():
    for folder in FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[OK] Created folder: {folder}")
        else:
            print(f"[SKIP] Folder already exists: {folder}")

    print("\nEnvironment setup complete.")

if __name__ == "__main__":
    setup()
