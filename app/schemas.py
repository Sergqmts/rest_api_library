from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Пользователи (библиотекари)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

# Книги 
class BookCreate(BaseModel):
    title: str
    author: str
    year_published: Optional[int]
    isbn: Optional[str]
    quantity: Optional[int] = 1

class BookRead(BookCreate):
    id: int

    class Config:
        orm_mode = True

# Читатели 
class ReaderCreate(BaseModel):
    name: str
    email: EmailStr

class ReaderRead(ReaderCreate):
    id: int

# Выдача книги 
class BorrowBookRequest(BaseModel):
    book_id: int 
    reader_id: int 

# Возврат книги 
class ReturnBookRequest(BaseModel):
    book_id: int 
    reader_id: int 

# Токен JWT 
class Token(BaseModel):
    access_token: str 
    token_type: str 

# Токен с данными пользователя 
class TokenData(BaseModel):
    user_id: Optional[int]