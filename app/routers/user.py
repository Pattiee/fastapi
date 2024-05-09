from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas, utils, oath2
from ..database import engine, get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# USERS
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if users exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email or models.User.id_number == user.id_number).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Sorry {}!, it seems you had signed up before, please login or reset your "
                                   "password "
                                   "if forgot."
                            .format(user.first_name))
    # Hash the user password
    user.password = utils.hash_password(user.password)

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=schemas.UserResponse)
def get_user(db: Session = Depends(get_db),
             current_user: int = Depends(oath2.get_current_user)):
    user_id = current_user.id
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User id: {} not found".format(user_id))
    return user


@router.put("/", response_model=schemas.UserResponse)
def update_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oath2.get_current_user)):
    print("****************************************************")
    print(current_user)
    print("****************************************************")
    user = get_user(db, current_user)
    return {"data": user}
