import psycopg2
from typing import List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from psycopg2.extras import RealDictCursor
from .config import settings
import time
from .database import SessionLocal
from . import models, schemas, utils
from .database import engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True:
    try:
        conn = psycopg2.connect(host=f"{settings.fastapi_database_host}", database='fastapi3', user=f'{settings.fastapi_database_username}', password=f'{settings.fastapi_database_password}', cursor_factory=RealDictCursor)
        cur = conn.cursor()
        print('database connection successful')
        break
    except Exception as error:
        print('connection to database failed')
        print('error', error)
        time.sleep(2)

# def find_post(id):
#     cur.execute(""" SELECT * FROM posts WHERE id = %s""", (id))
#     post = cur.fetchone()
#     print(post)

@app.get("/sql", response_model=List[schemas.Post])
def sql_route(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.get("/sql/{id}", response_model=schemas.Post)
def sql_get_id(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return post

@app.delete("/sqldelete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def sql_delete(id: int, db: Session = Depends(get_db)):
  
   post = db.query(models.Post).filter(models.Post.id == id)
  
   if post.first() == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
   
   post.delete(synchronize_session=False)
   db.commit()
   return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/sqlupdate/{id}", response_model = schemas.Post)
def sql_update(updated_post: schemas.PostCreate, id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if not post:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

@app.post("/addsqluser", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def add_user(post: schemas.PostCreate, db: Session = Depends(get_db)):
   
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post



##### Psycopg2 Postgresql standard SQL Queries
@app.get("/")
def read_root():
    cur.execute(""" SELECT * FROM public.posts """)
    posts = cur.fetchall()
    print(posts)
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model = schemas.Post)
def create_post(post: schemas.PostCreate):
    cur.execute(""" INSERT into  public.posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cur.fetchone()
    conn.commit()
    return new_post

@app.get("/getpost/{id}")
def get_post(id: int):
    cur.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),))
    fetched_post = cur.fetchone()
    # post = find_post(id)
    if not fetched_post:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return fetched_post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cur.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate):
    cur.execute(""" UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, (str(id),)))
    updated_post = cur.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found.")
    
    return updated_post

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
   
    user = models.User(**user.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
   
@app.get("/users/{id}", response_model=schemas.User)
def get_users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()  

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found.") 

    return user


