from sqlalchemy.orm import Session

from models import Item
from schemas import ItemCreate, ItemUpdate


def create_item(db: Session, item: ItemCreate) -> Item:
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


