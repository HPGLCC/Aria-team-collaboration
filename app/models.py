from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone = Column(String(255))
    address = Column(String(255))
    role = Column(String(255), default="client")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 🔗 Relation avec CarteBancaire
    cartes_bancaires = relationship("CarteBancaire", back_populates="utilisateur", cascade="all, delete-orphan")


class CarteBancaire(Base):
    __tablename__ = "cartes_bancaires"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(255), nullable=False)
    date_expiration = Column(String(10), nullable=False)  # ex: MM/YY
    cvv = Column(String(4), nullable=False)
    nom_titulaire = Column(String(255), nullable=False)
    
    utilisateur_id = Column(String(255), ForeignKey("users.id"), nullable=False)

    # 🔁 Relation inverse
    utilisateur = relationship("User", back_populates="cartes_bancaires")
