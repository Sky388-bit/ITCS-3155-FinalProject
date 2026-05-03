from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import rewards as model
from ..models import customers as customer_model
from sqlalchemy.exc import SQLAlchemyError


def get_customer_rewards(db: Session, customer_id: int):
    """Get all rewards for a customer"""
    try:
        customer = db.query(customer_model.Customers).filter(customer_model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        rewards = db.query(model.Reward).filter(model.Reward.customer_id == customer_id).all()
        return rewards
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def get_unredeemed_rewards(db: Session, customer_id: int):
    """Get all unredeemed rewards for a customer"""
    try:
        customer = db.query(customer_model.Customers).filter(customer_model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        rewards = db.query(model.Reward).filter(
            model.Reward.customer_id == customer_id,
            model.Reward.is_redeemed == False
        ).all()
        return rewards
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def get_reward_summary(db: Session, customer_id: int):
    """Get reward summary for a customer"""
    try:
        customer = db.query(customer_model.Customers).filter(customer_model.Customers.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
        
        total_earned = db.query(model.Reward).filter(
            model.Reward.customer_id == customer_id,
            model.Reward.is_redeemed == False
        ).all()
        
        return {
            "customer_id": customer_id,
            "current_points": customer.reward_points,
            "total_rewards": len(total_earned)
        }
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
