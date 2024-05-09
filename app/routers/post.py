from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from .. import models, schemas, utils, oath2
from ..database import engine, get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# 1. Create Post
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db),
                current_user: int = Depends(oath2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# 2. Find all posts
@router.get("/", response_model=List[schemas.PostOut], status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oath2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    # To get all posts
    # NOTE: result = db.query(models.Post).filter(
    # ...models.Post.title.contains()).limit(...number).offset(...number).all()
    # posts = db.query(models.Post).filter(
    #     models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes"))\
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # TODO get user-specific posts
    # user_specific_posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    return posts


# 3. Find post by id
@router.get("/{q}", response_model=schemas.PostOut, status_code=status.HTTP_302_FOUND)
def get_post(q: int, db: Session = Depends(get_db),
             current_user: int = Depends(oath2.get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == q).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id)\
        .filter(models.Post.id == q).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {q} not found!")

    # TODO: The lines below may be commented to allow content for public.
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Unauthorized content!")
    return post


# 4. Update/Patch post
@router.put("/{post_id}", response_model=schemas.PostResponse, status_code=status.HTTP_202_ACCEPTED)
def update_post(post_id: int, updated_post: schemas.CreatePost,
                db: Session = Depends(get_db),
                current_user: int = Depends(oath2.get_current_user)):
    # cursor.execute("""UPDATE posts SET
    # title = %s, content = %s, published = %s, ratings = %s WHERE id = %s RETURNING
    # *""", (post.title, post.content, post.published, post.rating, str(post_id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found!")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action!")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


# 5. Delete all posts
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_posts(db: Session = Depends(get_db),
                     current_user: int = Depends(oath2.get_current_user)):
    # To get user-specific posts
    user_specific_posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id)


# 6. Delete post by ID
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, response: Response,
                db: Session = Depends(get_db),
                current_user: int = Depends(oath2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(post_id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found!")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action!")

    post_query.delete(synchronize_session=False)
    db.commit()
