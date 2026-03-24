from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from schemas import ItemCreate, ItemUpdate, ItemResponse
from crud import create_item, get_items, get_item, update_item, delete_item

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", response_model=ItemResponse)
def create(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db=db, item=item)


@app.get("/items", response_model=list[ItemResponse])
def read_all(db: Session = Depends(get_db)):
    return get_item(db=db)


