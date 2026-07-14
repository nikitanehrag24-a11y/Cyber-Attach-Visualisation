"""
CyberVision Dashboard Orchestration Wrapper.
Redirects execution to the root app.py to unify deployment logic.
"""

import sys
from pathlib import Path

# Add project root to the beginning of python path to prevent importing other PyPI 'app' packages
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Import main orchestrator from the root app.py
from app import main

if __name__ == "__main__":
    main()
