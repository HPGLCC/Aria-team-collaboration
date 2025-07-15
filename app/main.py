from fastapi import FastAPI
from app.routes import users
from app.database import create_db_and_tables
from app.routes import users, cartes  # ← ajoute cartes



app = FastAPI(title="Aria Auth API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Route d'accueil pour éviter l'erreur 404 à la racine "/"
@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API Aria Team Collaboration 🎉"}

# Inclusion du routeur des utilisateurs
app.include_router(users.router, prefix="/users", tags=["Auth"])
app.include_router(cartes.router, prefix="/cartes", tags=["Cartes Bancaires"])

