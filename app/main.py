from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Base
from app.schemas import *
from app.crud import *
from app.auth import *
from app.dependencies import get_db
from app.config import SECRET_KEY

app = FastAPI()


# Создание таблиц при запуске
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Регистрация пользователя (библиотекаря)
@app.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# Вход (логин) и получение токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


# Защищенные маршруты — управление книгами
@app.post("/books/", response_model=BookRead)
async def create_book(book_in: BookCreate, db: AsyncSession = Depends(get_db),
                      current_user: int = Depends(get_current_user)):
    new_book = Book(**book_in.dict())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


# Аналогично реализуйте CRUD для книг (GET /books/, GET /books/{id}, PUT /books/{id}, DELETE /books/{id})

# Управление читателями — аналогично

# Выдача книги
@app.post("/borrow/")
async def borrow_book(borrow_in: BorrowRequest, db: AsyncSession = Depends(get_db),
                      current_user: int = Depends(get_current_user)):
    book_obj = await get_book_by_id(db, borrow_in.book_id)
    reader_obj = await get_reader_by_id(db, borrow_in.reader_id)

    if not book_obj or not reader_obj:
        raise HTTPException(status_code=404, detail="Book or Reader not found")

    available_copies = book_obj.quantity
    if available_copies <= 0:
        raise HTTPException(status_code=400, detail="No available copies")

    # Проверка количества книг у читателя
    borrowed_count_query = select(BorrowedBook).where(
        BorrowedBook.reader_id == borrow_in.reader_id,
        BorrowedBook.return_date.is_(None)
    )
    result_borrowed_count = await db.execute(borrowed_count_query)
    borrowed_books_count = len(result_borrowed_count.scalars().all())

    if borrowed_books_count >= 3:
        raise HTTPException(status_code=400, detail="Reader has already borrowed maximum number of books")

    # Уменьшаем количество экземпляров
    book_obj.quantity -= 1

    borrowed_record = new
    BorrowedBook(
        book_id=borrow_in.book_id,
        reader_id=borrow_in.reader_id,
        borrow_date=datetime.utcnow(),
        return_date=None
    )

    db.add(borrowed_record