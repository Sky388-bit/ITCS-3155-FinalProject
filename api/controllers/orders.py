import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import orders as model
from sqlalchemy.exc import SQLAlchemyError

def generate_tracking_number():
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"

def create(db: Session, request):
    if not request.customers_id and not (request.customers_name and request.customers_email and request.customers_phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Guest orders require a name, email, and phone number")

    if request.order_type == "Delivery" and not request.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Delivery orders require an address in the description")
    new_item = model.Order(
        customers_id=request.customers_id,
        customers_name=request.customers_name,
        customers_email=request.customers_email,
        customers_phone=request.customers_phone,
        tracking_number=generate_tracking_number(),
        order_status=request.order_status or "Placed",
        description=request.description,
        total_price=request.total_price or 0.0,
        order_type=request.order_type,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session, start_date=None, end_date=None):
    try:
        query = db.query(model.Order)

        if start_date:
            query = query.filter(model.Order.order_date >= start_date)
        if end_date:
            query = query.filter(model.Order.order_date <= end_date)
        result = query.all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
