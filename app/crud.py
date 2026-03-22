from sqlalchemy.orm import Session

from models import Item
from schemas import ItemCreate, ItemUpdate


def create_item(db: Session, item: ItemCreate) -> Item:
    db_item = Item(name=item.name, description=item.description)
    db.add(instance=db_item)
    db.commit()
    db.refresh(instance=db_item)
    return db_item


def get_items(db: Session) -> list[Item]:
    return db.query(Item).all()


def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


def update_item(db: Session, item_id: int, item: ItemUpdate) -> Item | None:
    db_item = db.query(Item).filter(Item.id == item_id).first()

    if not db_item:
        return None

    if item.name is not None:
        db_item.name = item.name

    if item.description is not None:
        db_item.description = item.description

    db.commit()
    db.refresh(instance=db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    db_item = db.query(Item).filter(Item.id == item_id).first()

    if not db_item:
        return False

    db.delete(instance=db_item)
    db.commit()
    return True