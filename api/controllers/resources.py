from sqlalchemy.orm import Session
from fastapi import status, HTTPException, Response
from ..models import resources as model
from ..schemas import resources as schema
from sqlalchemy.exc import SQLAlchemyError

def create(db: Session, request):
    new_item = model.Resource(
        item=request.item,
        amount=request.amount,
        min_threshold=request.min_threshold
    )
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return new_item

def read_all(db: Session):
    try:
        result = db.query(model.Resource).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return result

def read_one(db: Session, resource_id: int):
    try:
        result = db.query(model.Resource).filter(model.Resource.id == resource_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return result

def update(db: Session, item_id, request):
    try:
        item = db.query(model.Resource).filter(model.Resource.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Id not found!")

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return item

def delete(db: Session, resource_id: int):
    try:
        item = db.query(model.Resource).filter(model.Resource.id == resource_id)
        if not item.first():
            raise HTTPException(status_code=404, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

def get_low_stock(db: Session):
    try:
        result = db.query(model.Resource).filter(model.Resource.amount < model.Resource.min_threshold).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)
    return result