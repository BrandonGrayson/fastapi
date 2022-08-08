from .. import models, schemas, utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
   
    user = models.User(**user.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
   
@router.get("/users/{id}", response_model=schemas.User)
def get_users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()  

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found.") 

    return user
