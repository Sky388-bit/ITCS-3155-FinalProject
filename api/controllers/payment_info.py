from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import payment_info as model, orders
from sqlalchemy.exc import SQLAlchemyError

def create(db: Session, request):
    order = db.query(orders.Order).filter(orders.Order.id == request.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    new_payment_info = model.PaymentInfo(
        transaction_status=request.transaction_status,
        payment_type=request.payment_type,
        amount=request.amount,
        order_id=request.order_id,
    )

    try:
        db.add(new_payment_info)
        # Find all past payments on the order and add them up
        all_payments = db.query(model.PaymentInfo).filter(
            model.PaymentInfo.order_id == request.order_id,
            model.PaymentInfo.transaction_status == "Success",
            model.PaymentInfo.id != new_payment_info.id,
        ).all()
        total_paid = sum(p.amount for p in all_payments)

        current_amount = request.amount if request.transaction_status == "Success" else 0

        order_price = db.query(orders.Order).filter(orders.Order.id == request.order_id).first()
        if (total_paid + current_amount) >= order.total_price:
            order.order_status = "Paid"
        db.commit()
        db.refresh(new_payment_info)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_payment_info

def read_all(db: Session):
    try:
        result = db.query(model.PaymentInfo).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result

def read_one(db: Session, item_id):
    try:
        result = db.query(model.PaymentInfo).filter(model.PaymentInfo.id == item_id).first()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result

def update(db: Session, item_id, request):
    try:
        item = db.query(model.PaymentInfo).filter(model.PaymentInfo.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db, item_id):
    try:
        item = db.query(model.PaymentInfo).filter(model.PaymentInfo.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)