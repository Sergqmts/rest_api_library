from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from .auth import verify_token

def get_db():
     db= SessionLocal()
     try:
         yield db
     finally:
         db.close()

def get_current_user(token:str=Depends(...)):  # позже добавим зависимость для получения токена
     user_id= verify_token(token)
     if user_id is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid authentication credentials")
     return user_id
