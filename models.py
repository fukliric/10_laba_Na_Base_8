from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class BookDB(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    isbn = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BookDB(id={self.id}, title='{self.title}', author='{self.author}')>"