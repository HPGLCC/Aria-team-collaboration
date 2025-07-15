from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.token import get_current_user

router = APIRouter(
    prefix="/cartes",
    tags=["Cartes Bancaires"]
)

# Ajouter une carte bancaire
@router.post("/", response_model=schemas.CarteBancaireOut)
def ajouter_carte_bancaire(
    carte: schemas.CarteBancaireCreate,
    db: Session = Depends(get_db),
    utilisateur: models.User = Depends(get_current_user)
):
    nouvelle_carte = models.CarteBancaire(
        numero=carte.numero,
        date_expiration=carte.date_expiration,
        cvv=carte.cvv,
        nom_titulaire=carte.nom_titulaire,
        utilisateur_id=utilisateur.id
    )
    db.add(nouvelle_carte)
    db.commit()
    db.refresh(nouvelle_carte)
    return nouvelle_carte

# Récupérer toutes les cartes de l’utilisateur connecté
@router.get("/", response_model=list[schemas.CarteBancaireOut])
def get_cartes_utilisateur(
    db: Session = Depends(get_db),
    utilisateur: models.User = Depends(get_current_user)
):
    return db.query(models.CarteBancaire).filter_by(utilisateur_id=utilisateur.id).all()
