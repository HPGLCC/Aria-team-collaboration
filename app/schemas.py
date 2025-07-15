
from pydantic import BaseModel, EmailStr,Field
from typing import Optional

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str   
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    role: str
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True
#  Pour mettre à jour le profil utilisateur
class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]

#  Pour changer de mot de passe
class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class PasswordChangeFlexible(BaseModel):
    old_password: Optional[str] = None
    new_password: str = Field(..., min_length=8)


# Schéma pour la carte bancaire - lecture seule (GET)
class CarteBancaireOut(BaseModel):
    id: int
    numero: str
    date_expiration: str
    nom_titulaire: str

    class Config:
        orm_mode = True
        from_attributes = True

# Schéma pour la création d’une carte bancaire (POST)
class CarteBancaireCreate(BaseModel):
    numero: str
    date_expiration: str
    cvv: str
    nom_titulaire: str


class CarteUpdate(BaseModel):
    numero: Optional[str]
    date_expiration: Optional[str]
    cvv: Optional[str]
    nom_titulaire: Optional[str]
       
    class Config:
        orm_mode = True

