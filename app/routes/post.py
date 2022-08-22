from .. import models, schemas
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from typing import List

router = APIRouter(
    prefix= '/posts',
    tags=["Posts"]
)

# Last thing done was updated the limit for the get route

@router.get("/", response_model=List[schemas.Post])
def sql_route(db: Session = Depends(get_db), limit: int = 10):
    posts = db.query(models.Post).limit(limit).all()
    return posts

@router.get("/{id}", response_model=schemas.Post)
def sql_get_id(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def sql_delete(id: int, db: Session = Depends(get_db)):
  
   post = db.query(models.Post).filter(models.Post.id == id)
  
   if post.first() == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
   
   post.delete(synchronize_session=False)
   db.commit()
   return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = schemas.Post)
def sql_update(updated_post: schemas.PostCreate, id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if not post:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def add_user(post: schemas.PostCreate, db: Session = Depends(get_db)):
    print('post', post)
    owner_id = input("What is the owner id for this post?")
    int(owner_id)
    new_post = models.Post(owner_id=owner_id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
