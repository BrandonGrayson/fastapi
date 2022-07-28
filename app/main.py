from ast import While
import psycopg2
from typing import Union
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
from psycopg2.extras import RealDictCursor
from .config import settings
import time
from .database import SessionLocal
from . import models
from .database import engine
from sqlalchemy.orm import Session

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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

@app.get("/sqlalchemy")
def sql_route(db: Session = Depends(get_db)):
    return{"status": "Success"}

@app.get("/")
def read_root():
    cur.execute(""" SELECT * FROM public.posts """)
    posts = cur.fetchall()
    print(posts)
    return {"data": posts}

@app.post("/posts")
def create_post(post: Post):
    cur.execute(""" INSERT into  public.posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cur.fetchone()
    conn.commit()
    return {"new post": new_post}

@app.get("/getpost/{id}")
def get_post(id: int):
    cur.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),))
    fetched_post = cur.fetchone()
    # post = find_post(id)
    if not fetched_post:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"ind_post": fetched_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cur.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cur.execute(""" UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, (str(id),)))
    updated_post = cur.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found.")
    
    return {"updated_post": updated_post}

