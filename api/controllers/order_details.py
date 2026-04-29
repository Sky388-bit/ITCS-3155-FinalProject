from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import order_details as model, recipes, resources, menu, orders
from sqlalchemy.exc import SQLAlchemyError


def create(db: Session, request):
    # Find and deduct resources if possible
    recipe_items = db.query(recipes.Recipe).filter(recipes.Recipe.menu_id == request.menu_id).all()
    for item in recipe_items:
        resource = db.query(resources.Resource).filter(resources.Resource.id == item.resource_id).first()
        if not resource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        if resource.amount < item.amount * request.amount:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not enough {resource.item} in stock.")
        else:
            resource.amount -= item.amount * request.amount

    new_item = model.OrderDetail(
        order_id=request.order_id,
        menu_id=request.menu_id,
        amount=request.amount
    )

    try:
        db.add(new_item)
        # Update Order Total
        dish = db.query(menu.Menu).filter(menu.Menu.id == request.menu_id).first()
        order = db.query(orders.Order).filter(orders.Order.id == request.order_id).first()
        if order and dish:
            order.total_price = (order.total_price or 0) + (dish.price * request.amount)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.OrderDetail).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
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
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
