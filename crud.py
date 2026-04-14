from sqlalchemy.orm import Session
from models import BookDB
from schemas import BookCreate, BookUpdate
from datetime import datetime

def get_all_books(db: Session):
    return db.query(BookDB).all()

def search_books_by_title(db: Session, title: str):
    return db.query(BookDB).filter(BookDB.title.ilike(f"%{title}%")).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(BookDB).filter(BookDB.id == book_id).first()

def create_book(db: Session, book: BookCreate):
    db_book = BookDB(**book.dict(), created_at=datetime.utcnow())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: BookUpdate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True