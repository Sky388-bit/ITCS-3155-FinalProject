from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import rewards as controller
from ..schemas import rewards as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=['Rewards'],
    prefix="/rewards"
)


@router.get("/customers/{customer_id}/history")
def get_customer_rewards(customer_id: int, db: Session = Depends(get_db)):
    """Get all rewards history for a customer"""
    return controller.get_customer_rewards(db=db, customer_id=customer_id)


@router.get("/customers/{customer_id}/unredeemed")
def get_unredeemed_rewards(customer_id: int, db: Session = Depends(get_db)):
    """Get all unredeemed rewards for a customer"""
    return controller.get_unredeemed_rewards(db=db, customer_id=customer_id)


@router.get("/customers/{customer_id}/summary")
def get_reward_summary(customer_id: int, db: Session = Depends(get_db)):
    """Get reward summary for a customer"""
    return controller.get_reward_summary(db=db, customer_id=customer_id)
