from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CarteBancaire, User
from app.schemas import CarteBancaireCreate, CarteBancaireOut, CarteUpdate
from app.utils.token import get_current_user

router = APIRouter(
    prefix="/cartes",
    tags=["Cartes Bancaires"]
)

# 🔐 Ajouter une carte bancaire pour l'utilisateur connecté
@router.post("/", response_model=CarteBancaireOut)
def ajouter_carte_bancaire(
    carte: CarteBancaireCreate,
    db: Session = Depends(get_db),
    utilisateur: User = Depends(get_current_user)
):
    nouvelle_carte = CarteBancaire(
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

# 📥 Récupérer toutes les cartes de l'utilisateur connecté
@router.get("/", response_model=list[CarteBancaireOut])
def get_cartes_utilisateur(
    db: Session = Depends(get_db),
    utilisateur: User = Depends(get_current_user)
):
    return db.query(CarteBancaire).filter_by(utilisateur_id=utilisateur.id).all()

# 🗑 Supprimer une carte par ID
@router.delete("/{carte_id}", status_code=204)
def supprimer_carte(
    carte_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    carte = db.query(CarteBancaire).filter(CarteBancaire.id == carte_id, CarteBancaire.utilisateur_id == user.id).first()
    if not carte:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    db.delete(carte)
    db.commit()
    return

# ✏️ Mettre à jour une carte
@router.put("/{carte_id}", response_model=CarteBancaireOut)
def mettre_a_jour_carte(
    carte_id: int,
    data: CarteUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    carte = db.query(CarteBancaire).filter(CarteBancaire.id == carte_id, CarteBancaire.utilisateur_id == user.id).first()
    if not carte:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(carte, field, value)
    
    db.commit()
    db.refresh(carte)
    return carte

# 🔍 Récupérer les cartes d'un utilisateur spécifique (admin uniquement ou soi-même)
@router.get("/user/{user_id}", response_model=list[CarteBancaireOut])
def cartes_par_utilisateur_id(
    user_id: str,
    db: Session = Depends(get_db),
    utilisateur: User = Depends(get_current_user)
):
    if utilisateur.role != "admin" and utilisateur.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit")
    
    return db.query(CarteBancaire).filter_by(utilisateur_id=user_id).all()
