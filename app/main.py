from fastapi import FastAPI
from app.routes import users
from app.database import create_db_and_tables

app = FastAPI(title="Aria Auth API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(users.router, prefix="/users", tags=["Auth"])
