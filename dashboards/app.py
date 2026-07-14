"""
CyberVision Dashboard Orchestration Wrapper.
Redirects execution to the root app.py to unify deployment logic.
"""

import sys
from pathlib import Path

# Add project root to python path to support importing root modules and pages
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Import main orchestrator from the root app.py
from app import main

if __name__ == "__main__":
    main()
