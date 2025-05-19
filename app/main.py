from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from config import engine
from dependencies import get_db

import datetime

models.Base.metadata.create_all(bind=engine)

app= FastAPI()

# --- Регистрация и логин ---

@app.post("/register", response_model=schema.UserRead)
def register(user_in:schema.UserCreate , db:Session=Depends(get_db)):
     # Проверка уникальности email
     existing_user= db.query(models.User).filter(models.User.email==user_in.email).first()
     if existing_user:
         raise HTTPException(status_code=400 , detail="Email already registered")
     
     from passlib.context import CryptContext
     pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
     
     hashed_password= pwd_context.hash(user_in.password)
     
     new_user= models.User(email=user_in.email , hashed_password=hashed_password)
     db.add(new_user)
     db.commit()
     db.refresh(new_user)
     return new_user

@app.post("/login", response_model=schema.Token)
def login(user_in:schema.UserCreate , db:Session=Depends(get_db)):
     user= db.query(models.User).filter(models.User.email==user_in.email).first()
     if not user:
         raise HTTPException(status_code=400 , detail="Incorrect email or password")
     
     from passlib.context import CryptContext
     pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
     
     if not pwd_context.verify(user_in.password , user.hashed_password):
         raise HTTPException(status_code=400 , detail="Incorrect email or password")
     
     access_token= simple_auth.create_access_token(data={"sub":str(user.id)})
     
     return {"access_token": access_token , "token_type": "bearer"}

# --- Защищенные эндпоинты ---

def get_token_from_header(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

def get_current_user(token: str = Depends(get_token_from_header)):
    try:
        payload = simple_auth.decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/books/", response_model=schema.BookRead)
def create_book(
    book_in: schema.BookCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    # current_user — это id пользователя
    book = models.Book(**book_in.dict(), owner_id=current_user)  # если есть поле owner_id
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@app.get("/books/", response_model=List[schema.BookRead])
def read_books(db:Session=Depends(get_db)):
      books=db.query(models.Book).all()
      return books