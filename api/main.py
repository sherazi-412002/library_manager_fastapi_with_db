from fastapi import FastAPI,HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session,select
from api import settings
from typing import List
 


# Create Model

class Book(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str 
    author: str
    year: int
    genre: str
    read: bool


# Create Engine

connection_string: str= str(settings.DATABASE_URL).replace("postgresql","postgresql+psycopg2")
engine = create_engine(connection_string, connect_args={"sslmode":"require"},pool_recycle=300,pool_size=10,echo=False)


SQLModel.metadata.create_all(engine)

# book1 = Book(title='urdu',author='allama iqbal',year=2025,genre='course',read=True)
# book2 = Book(title='english',author='abcde',year=2022,genre='course',read=False)


# Session :: seperate session for each functionality
session = Session(engine)

# create books in database
# session.add(book1)
# session.add(book2)
# print(f"Before Commit {book1}")
# session.commit()
# print(f"After Commit {book1}")
# session.close()




app : FastAPI = FastAPI()

@app.get("/")
async def root ():
    return {"message":"Welcome To Personal Library Manager"}



@app.post("/books/", response_model=Book)
def create_book(book: Book):
    with Session(engine) as session:
        db_book = Book(**book.dict())
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book

@app.get("/books/", response_model=List[Book])
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

@app.delete("/books/{book_id}", response_model=Book)
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
        return book
