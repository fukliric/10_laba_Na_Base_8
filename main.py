from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Импорты из 4-й лабы
from database import engine, Base, get_db
from models import BookDB
from schemas import BookCreate, BookUpdate, BookResponse
from crud import (
    get_all_books, search_books_by_title, create_book,
    update_book, delete_book, get_book_by_id
)

# Импорт планировщика
from scheduler import start_scheduler

# Создаём таблицы (при первом запуске)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при запуске
    scheduler = start_scheduler()
    yield
    # Действия при остановке
    scheduler.shutdown()
    print("Планировщик остановлен")

app = FastAPI(title="Объединённое API (лаб.3 + лаб.4)", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 3-я лабораторная (in-memory) ==========
bookshelf: Dict[int, Dict[str, Any]] = {
    1: {'book': 'Ulyss', 'price': 4.75, 'author': 'James Joyce'},
    2: {'book': 'Three Men in a Boat (To Say Nothing of the Dog)', 'price': 3.99, 'author': 'Jerome K. Jerome'}
}

movies: Dict[str, Dict[str, Any]] = {
    "inception": {"title": "Inception", "year": 2010, "rating": 8.8},
    "matrix": {"title": "The Matrix", "year": 1999, "rating": 8.7}
}

class BookInfo(BaseModel):
    book: str
    price: float
    author: Optional[str] = None

class UpdateBookMem(BaseModel):
    book: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None

class MovieInfo(BaseModel):
    title: str
    year: int
    rating: float

class UpdateMovie(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None

@app.get('/')
async def home():
    return {'message': 'Добро пожаловать в API! Используйте /docs для тестирования.'}

@app.get('/now')
async def get_current_time():
    return {'current_datetime': datetime.now().isoformat(), 'timestamp': datetime.now().timestamp()}

@app.get('/get-book/{book_id}')
async def get_book(book_id: int):
    if book_id not in bookshelf:
        return {'Error': 'Book not found'}
    return bookshelf[book_id]

@app.post('/create-book/{book_id}')
async def create_book_in_memory(book_id: int, new_book: BookInfo):
    if book_id in bookshelf:
        return {'Error': 'Book already exists'}
    bookshelf[book_id] = new_book.dict()
    return bookshelf[book_id]

@app.put('/update-book/{book_id}')
async def update_book_in_memory(book_id: int, upd_book: UpdateBookMem):
    if book_id not in bookshelf:
        return {'Error': 'Book ID does not exist'}
    if upd_book.book is not None:
        bookshelf[book_id]['book'] = upd_book.book
    if upd_book.price is not None:
        bookshelf[book_id]['price'] = upd_book.price
    if upd_book.author is not None:
        bookshelf[book_id]['author'] = upd_book.author
    return bookshelf[book_id]

@app.delete('/delete-book')
def delete_book_in_memory(book_id: int = Query(..., ge=1)):
    if book_id not in bookshelf:
        return {'Error': 'Book ID does not exist'}
    del bookshelf[book_id]
    return {'Done': 'The book successfully deleted'}

@app.get('/movies')
async def get_all_movies():
    return movies

@app.get('/get-movie/{key}')
async def get_movie(key: str):
    if key not in movies:
        return {'Error': 'Movie not found'}
    return movies[key]

@app.post('/create-movie/{key}')
async def create_movie(key: str, new_movie: MovieInfo):
    if key in movies:
        return {'Error': 'Movie with this key already exists'}
    movies[key] = new_movie.dict()
    return movies[key]

@app.put('/update-movie/{key}')
async def update_movie(key: str, upd_movie: UpdateMovie):
    if key not in movies:
        return {'Error': 'Movie key does not exist'}
    if upd_movie.title is not None:
        movies[key]['title'] = upd_movie.title
    if upd_movie.year is not None:
        movies[key]['year'] = upd_movie.year
    if upd_movie.rating is not None:
        movies[key]['rating'] = upd_movie.rating
    return movies[key]

@app.delete('/delete-movie')
def delete_movie(key: str = Query(...)):
    if key not in movies:
        return {'Error': 'Movie key does not exist'}
    del movies[key]
    return {'Done': 'Movie successfully deleted'}

# ========== 4-я лабораторная (PostgreSQL) ==========
@app.get("/books", response_model=list[BookResponse])
def read_all_books(db: Session = Depends(get_db)):
    return get_all_books(db)

@app.get("/books/search", response_model=list[BookResponse])
def search_books(title: str, db: Session = Depends(get_db)):
    return search_books_by_title(db, title)

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    if book.isbn:
        existing = db.query(BookDB).filter(BookDB.isbn == book.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    return create_book(db, book)

@app.put("/books/{book_id}", response_model=BookResponse)
def modify_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    updated = update_book(db, book_id, book_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(book_id: int, db: Session = Depends(get_db)):
    success = delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return