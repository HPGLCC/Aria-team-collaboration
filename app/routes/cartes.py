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



@router.delete("/{carte_id}", status_code=204)
def supprimer_carte(carte_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    carte = db.query(CarteBancaire).filter(CarteBancaire.id == carte_id, CarteBancaire.utilisateur_id == user.id).first()
    if not carte:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    db.delete(carte)
    db.commit()


class CarteUpdate(BaseModel):
    numero: Optional[str]
    date_expiration: Optional[str]
    cvv: Optional[str]
    nom_titulaire: Optional[str]

@router.put("/{carte_id}", response_model=CarteOut)
def mettre_a_jour_carte(carte_id: int, data: CarteUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    carte = db.query(CarteBancaire).filter(CarteBancaire.id == carte_id, CarteBancaire.utilisateur_id == user.id).first()
    if not carte:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(carte, field, value)
    db.commit()
    db.refresh(carte)
    return carte


@router.get("/user/{user_id}", response_model=list[schemas.CarteBancaireOut])
def cartes_par_utilisateur_id(
user_id: str,
db: Session = Depends(get_db),
utilisateur: models.User = Depends(get_current_user)
):
if utilisateur.role != "admin" and utilisateur.id != user_id:
raise HTTPException(status_code=403, detail="Accès interdit")
return db.query(models.CarteBancaire).filter_by(utilisateur_id=user_id).all()
