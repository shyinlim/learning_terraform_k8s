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
