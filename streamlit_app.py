"""
Entry point for Streamlit Community Cloud and Hugging Face Spaces.
"""
import sys
from pathlib import Path

# Add project root to path so imports work
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

import streamlit as st

# Import main app
from app.main import main

if __name__ == "__main__":
    main()
