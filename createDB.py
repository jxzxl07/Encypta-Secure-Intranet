from src.database import initialize_database


if __name__ == "__main__":
    db_path = initialize_database()
    print(f"Database ready at {db_path}")
