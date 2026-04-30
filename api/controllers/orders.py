import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import orders as model, menu as menu_model, order_details as detail_model
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


def read_one_by_tracking_number(db: Session, tracking_number):
    try:
        item = db.query(model.Order).filter(model.Order.tracking_number == tracking_number).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking number not found!")
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

def get_item_revenue(db: Session, menu_id: int =None, start_date=None, end_date=None):
    try:
        query = (db.query(detail_model.OrderDetail).join(model.Order).
                filter(detail_model.OrderDetail.menu_id == menu_id))
        if start_date:
            query = query.filter(model.Order.order_date >= start_date)
        if end_date:
            query = query.filter(model.Order.order_date <= end_date)

        details = query.all()
        dish = db.query(menu_model.Menu).filter(menu_model.Menu.id == menu_id).first()

        total_revenue = sum(d.amount * dish.price for d in details) if dish else 0.0
        return {
            "menu_item": dish.dish_name if dish else "Unknown",
            "total_revenue": total_revenue,
            "total_sold": sum(d.amount for d in details)
        }
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

def get_total_revenue(db: Session, start_date=None, end_date=None):
    try:
        query = db.query(model.Order)

        if start_date:
            query = query.filter(model.Order.order_date >= start_date)
        if end_date:
            query = query.filter(model.Order.order_date <= end_date)
        order = query.all()
        total_revenue = sum(order.total_price for order in order if order.total_price)

        return {
            "total_revenue": total_revenue,
            "order_count": len(order),
        }
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)