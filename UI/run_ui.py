#!/usr/bin/env python3
"""
Simple runner for the UI application
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Change to UI directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Starting CFR UI Authentication System...")
    print("Make sure you have run: python scripts/setup_auth.py")
    print()

    # Run the app
    subprocess.run([sys.executable, "app.py"])
