from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import customers as model
from ..models import favorite_orders as fav_model
from ..models import rewards as reward_model
from ..models import orders as order_model
from ..dependencies.security import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date


def create(db: Session, request):
    # Hash the password before storing
    hashed_password = hash_password(request.password)
    
    new_item = model.Customers(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        address=request.address,
        password=hashed_password,
        birthday=request.birthday,
        reward_points=0
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Customers).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Customers).filter(model.Customers.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Customers).filter(model.Customers.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Customers).filter(model.Customers.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def change_password(db: Session, customer_id: int, old_password: str, new_password: str):
    """Change customer password"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        # Verify old password
        if not verify_password(customer.password, old_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password!")
        
        # Hash and update new password
        customer.password = hash_password(new_password)
        db.commit()
        db.refresh(customer)
        return customer
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def get_order_history(db: Session, customer_id: int):
    """Get all orders for a customer"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        orders = db.query(order_model.Order).filter(order_model.Order.customers_id == customer_id).all()
        return orders
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def add_favorite_order(db: Session, customer_id: int, order_id: int):
    """Add an order to customer's favorites"""
    try:
        # Verify customer exists
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        # Verify order exists and belongs to customer
        order = db.query(order_model.Order).filter(
            order_model.Order.id == order_id,
            order_model.Order.customers_id == customer_id
        ).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or does not belong to this customer!")
        
        # Check if already favorited
        existing = db.query(fav_model.FavoriteOrder).filter(
            fav_model.FavoriteOrder.customer_id == customer_id,
            fav_model.FavoriteOrder.order_id == order_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already in favorites!")
        
        # Add to favorites
        favorite = fav_model.FavoriteOrder(customer_id=customer_id, order_id=order_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def remove_favorite_order(db: Session, customer_id: int, order_id: int):
    """Remove an order from customer's favorites"""
    try:
        favorite = db.query(fav_model.FavoriteOrder).filter(
            fav_model.FavoriteOrder.customer_id == customer_id,
            fav_model.FavoriteOrder.order_id == order_id
        ).first()
        
        if not favorite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found!")
        
        db.delete(favorite)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def get_favorite_orders(db: Session, customer_id: int):
    """Get all favorite orders for a customer"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        favorites = db.query(fav_model.FavoriteOrder).filter(
            fav_model.FavoriteOrder.customer_id == customer_id
        ).all()
        return favorites
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def add_reward_points(db: Session, customer_id: int, points: int, reward_type: str = "purchase", order_id: int = None):
    """Add reward points to a customer"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        # Update customer reward points
        customer.reward_points += points
        
        # Record the reward transaction
        reward = reward_model.Reward(
            customer_id=customer_id,
            order_id=order_id,
            points_earned=points,
            reward_type=reward_type
        )
        
        db.add(reward)
        db.commit()
        db.refresh(customer)
        return customer
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def redeem_reward_points(db: Session, customer_id: int, points_to_redeem: int):
    """Redeem reward points"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        if customer.reward_points < points_to_redeem:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient reward points!")
        
        # Update customer reward points
        customer.reward_points -= points_to_redeem
        
        # Record the redemption
        reward = reward_model.Reward(
            customer_id=customer_id,
            points_earned=-points_to_redeem,
            reward_type="redemption",
            is_redeemed=True,
            redemption_date=datetime.now()
        )
        
        db.add(reward)
        db.commit()
        db.refresh(customer)
        return customer
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def check_birthday_reward(db: Session, customer_id: int):
    """Check and award birthday reward if applicable"""
    try:
        customer = db.query(model.Customers).filter(model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        if not customer.birthday:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No birthday set for this customer!")
        
        today = date.today()
        is_birthday = (customer.birthday.month == today.month and customer.birthday.day == today.day)
        
        if is_birthday:
            # Award birthday reward (free cookie = 50 points)
            return add_reward_points(db, customer_id, 50, "birthday")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Today is not the customer's birthday!")
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
