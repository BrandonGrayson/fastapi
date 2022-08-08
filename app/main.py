import psycopg2

from fastapi import FastAPI, Response, status, HTTPException, Depends
from psycopg2.extras import RealDictCursor
from .config import settings
import time
from .database import SessionLocal
from . import models
from .database import engine
from .routes import users, post

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router)
app.include_router(post.router)

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

##### Psycopg2 Postgresql standard SQL Queries
# @app.get("/")
# def read_root():
#     cur.execute(""" SELECT * FROM public.posts """)
#     posts = cur.fetchall()
#     print(posts)
#     return posts

# @app.post("/posts", status_code=status.HTTP_201_CREATED, response_model = schemas.Post)
# def create_post(post: schemas.PostCreate):
#     cur.execute(""" INSERT into  public.posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
#     new_post = cur.fetchone()
#     conn.commit()
#     return new_post

# @app.get("/getpost/{id}")
# def get_post(id: int):
#     cur.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),))
#     fetched_post = cur.fetchone()
#     # post = find_post(id)
#     if not fetched_post:
#          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
#     return fetched_post

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
#     deleted_post = cur.fetchone()
#     conn.commit()

#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
#     return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.put("/posts/{id}")
# def update_post(id: int, post: schemas.PostCreate):
#     cur.execute(""" UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, (str(id),)))
#     updated_post = cur.fetchone()
#     conn.commit()

#     if updated_post == None:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found.")
    
#     return updated_post




