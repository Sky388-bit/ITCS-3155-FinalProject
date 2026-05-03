from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import menu as model
from sqlalchemy.exc import SQLAlchemyError
from ..schemas import menu as schema

def create(db: Session, request: schema.MenuCreate):
    new_item = model.Menu(
        dish_name= request.dish_name,
        dish_description= request.dish_description,
        price= request.price,
        calories= request.calories,
        category= request.category
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item

def read_all(db: Session, category: str = None, query: str = None):
    try:
        db_query = db.query(model.Menu)
        if category:
            db_query = db_query.filter(model.Menu.category == category)

        if query:
            db_query = db_query.filter(
                (model.Menu.dish_name.contains(query)) | (model.Menu.dish_description.contains(query))
            )
        items = db_query.all()
    except SQLAlchemyError as e:
        raise e

    return items

def read_one(db: Session, item_id: int):
    try:
        item = db.query(model.Menu).filter(model.Menu.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
    except SQLAlchemyError as e:
        raise e

    return item

def update(db: Session, item_id: int, request: schema.MenuUpdate):
    try:
        item = db.query(model.Menu).filter(model.Menu.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        update_data = request.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)
    except SQLAlchemyError as e:
        raise e

    return item

def delete(db: Session, item_id: int):
    try:
        item = db.query(model.Menu).filter(model.Menu.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        db.delete(item)
        db.commit()
    except SQLAlchemyError as e:
        raise e

    return Response(status_code=status.HTTP_204_NO_CONTENT)