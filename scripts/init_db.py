#!/usr/bin/env python3
"""Initialize the radar SQLite database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from radar.memory import init_db, DB_PATH

if __name__ == "__main__":
    init_db()
    print(f"✓ radar.db ready at {DB_PATH}")
