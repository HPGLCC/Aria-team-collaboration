import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 🔹 Charger les variables d'environnement (utile en local avec .env)
load_dotenv()

# 🔹 Récupérer la variable DATABASE_URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 🔸 Adapter l'URL pour SQLAlchemy si Render fournit "postgres://" (au lieu de "postgresql://")
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🔹 Créer l'engine SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 🔹 Créer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🔹 Base pour les classes ORM
Base = declarative_base()


# 🔸 Créer les tables à partir des modèles définis
def create_db_and_tables():
    from app import models  # importer ici pour éviter les références circulaires
    Base.metadata.create_all(bind=engine)


# 🔹 Fournir une session DB (utilisé dans les dépendances FastAPI)
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
