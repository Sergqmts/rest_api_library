from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Пользователи (библиотекари)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr

# Книги
class BookCreate(BaseModel):
    title: str
    author: str
    publication_year: Optional[int]
    isbn: Optional[str]
    quantity: Optional[int] = 1

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    publication_year: Optional[int]
    isbn: Optional[str]
    quantity: int

# Читатели
class ReaderCreate(BaseModel):
    name: str
    email: EmailStr

class ReaderRead(BaseModel):
    id: int
    name: str
    email: EmailStr

# Выдача книги
class BorrowRequest(BaseModel):
    book_id: int
    reader_id: int

# Возврат книги
class ReturnRequest(BaseModel):
    book_id: int