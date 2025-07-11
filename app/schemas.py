
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