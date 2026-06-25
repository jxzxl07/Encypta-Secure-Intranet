import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import initialize_database


if __name__ == "__main__":
    db_path = initialize_database()
    print(f"Database ready at {db_path}")
