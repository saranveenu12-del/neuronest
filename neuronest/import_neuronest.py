"""Wrapper to import and run the NeuroNest AI tool from the School Projects folder."""
import sys
from pathlib import Path

NEURONEST_PATH = Path(r"c:\Users\user\OneDrive\school projects\neuronest")

if not NEURONEST_PATH.exists():
    raise FileNotFoundError(f"NeuroNest folder not found: {NEURONEST_PATH}")

sys.path.insert(0, str(NEURONEST_PATH))

from main import main

if __name__ == "__main__":
    main()
