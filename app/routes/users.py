from fastapi.security import OAuth2PasswordRequestForm
from app.utils.token import create_access_token
from datetime import timedelta,datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.auth import get_current_user,optional_user
from app.database import SessionLocal
from app.utils.security import hash_password, verify_password, generate_uuid
from fastapi import Body
import uuid
from app.services.notification_service import send_notification
from fastapi.responses import JSONResponse
from app.models import User  # ou ton chemin vers User

from app.database import get_db

router = APIRouter()


# Dependency pour récupérer la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserProfile, status_code=201)
def register(user: schemas.UserRegistration, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Vérification basique du mot de passe
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (min 8 characters)")

    # Créer un nouvel utilisateur
    new_user = models.User(
        id=str(uuid.uuid4()),
        email=user.email,
        hashed_password=hash_password(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        address=user.address,
        username=user.username
    )

    # Sauvegarde dans la base de données
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Appel au service de notification
    try:
        full_name = f"{new_user.first_name} {new_user.last_name}"
        send_notification("registration", {
            "email": new_user.email,
            "name": full_name
        })
    except Exception as e:
        print(f"Erreur lors de l'envoi de la notification : {e}")

    return new_user





@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == form_data.username) | 
        (models.User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token_data = {"sub": user.id}
    token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type":"bearer"}
            

@router.get("/me", response_model=schemas.UserProfile)
def get_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile/{user_id}", response_model=schemas.UserProfile)
def update_profile(
    user_id: str,
    updated_data: schemas.UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = updated_data.first_name or user.first_name
    user.last_name = updated_data.last_name or user.last_name
    user.phone = updated_data.phone or user.phone
    user.address = updated_data.address or user.address

    db.commit()
    db.refresh(user)
    return user



#  METTRE À JOUR LE PROFIL DE L'UTILISATEUR CONNECTÉ
@router.put("/profile", response_model=schemas.UserProfile)
def update_profile(
    updated_data: schemas.UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Cherche l'utilisateur actuel dans la base de données
    user = db.query(models.User).filter(models.User.id == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Met à jour les champs si des nouvelles valeurs sont fournies
    user.first_name = updated_data.first_name or user.first_name
    user.last_name = updated_data.last_name or user.last_name
    user.phone = updated_data.phone or user.phone
    user.address = updated_data.address or user.address

    # Enregistre les modifications
    db.commit()
    db.refresh(user)

    return user

#  CHANGER DE MOT DE PASSE
@router.patch("/change-password", tags=["Authentication"])
def change_password(
    password_data: schemas.PasswordChangeFlexible,
    db: Session = Depends(get_db),
    current_user=Depends(optional_user)  # <- dépendance qui accepte None
):
    # Cas 1 : utilisateur connecté avec ancien mot de passe
    if current_user and password_data.old_password:
        user = db.query(models.User).filter(models.User.id == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password_data.old_password, user.hashed_password):
            raise HTTPException(status_code=403, detail="Old password is incorrect")

    # Cas 2 : utilisateur non connecté avec token de reset
    elif password_data.reset_token:
        try:
            payload = jwt.decode(password_data.reset_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            user = db.query(models.User).filter(models.User.id == user_id).first()
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid reset token")

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="You must provide either old_password or reset_token")

    # Vérifie la sécurité du nouveau mot de passe
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password too short (min 8 characters)")

    # Mise à jour
    user.hashed_password = hash_password(password_data.new_password)
    db.commit()

    # Notification
    try:
        requests.post("http://notification-service/notify", json={
            "type": "passwordChanged",
            "data": {
                "email": user.email,
                "name": user.name,
                "changeDate": datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        print(f"Notification failed: {e}")

    return {"message": "Password updated successfully"}


@router.get("/validate")
def validate_token(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "valid": True,
        "userId": current_user.id,
        "email": current_user.email
    }


@router.post("/logout", tags=["Authentication"])
def logout(current_user: User = Depends(get_current_user)):
    # Ici, tu peux faire des choses comme invalider le token côté base de données, s'il y a un système de blacklist.
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Déconnexion réussie"}
    )

#  SUPPRIMER LE COMPTE UTILISATEUR
@router.delete("/users/{userId}")
def delete_user_account(
    userId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != userId:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(models.User).filter(models.User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "Compte supprimé avec succès"}
