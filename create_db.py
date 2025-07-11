from app.database import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ Tables créées avec succès dans la base MySQL.")