from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import customers as controller
from ..schemas import customers as schema
from ..schemas import favorite_orders as fav_schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Customers'],
    prefix="/customers"
)

@router.post("/", response_model=schema.Customers)
def create(request: schema.CustomersCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Customers])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Customers)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Customers)
def update(item_id: int, request: schema.CustomersUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)


# Account Management Endpoints
@router.post("/{customer_id}/change-password", response_model=schema.Customers)
def change_password(customer_id: int, request: schema.PasswordChange, db: Session = Depends(get_db)):
    """Change customer password"""
    return controller.change_password(
        db=db,
        customer_id=customer_id,
        old_password=request.old_password,
        new_password=request.new_password
    )


@router.get("/{customer_id}/order-history")
def get_order_history(customer_id: int, db: Session = Depends(get_db)):
    """Get order history for a customer"""
    return controller.get_order_history(db=db, customer_id=customer_id)


# Favorite Orders Endpoints
@router.post("/{customer_id}/favorites/{order_id}", response_model=fav_schema.FavoriteOrder)
def add_favorite(customer_id: int, order_id: int, db: Session = Depends(get_db)):
    """Add an order to customer's favorites"""
    return controller.add_favorite_order(db=db, customer_id=customer_id, order_id=order_id)


@router.delete("/{customer_id}/favorites/{order_id}")
def remove_favorite(customer_id: int, order_id: int, db: Session = Depends(get_db)):
    """Remove an order from customer's favorites"""
    return controller.remove_favorite_order(db=db, customer_id=customer_id, order_id=order_id)


@router.get("/{customer_id}/favorites", response_model=list[fav_schema.FavoriteOrder])
def get_favorites(customer_id: int, db: Session = Depends(get_db)):
    """Get all favorite orders for a customer"""
    return controller.get_favorite_orders(db=db, customer_id=customer_id)


# Rewards Program Endpoints
@router.post("/{customer_id}/rewards/add-points", response_model=schema.Customers)
def add_reward_points(customer_id: int, points: int, reward_type: str = "purchase", order_id: int = None, db: Session = Depends(get_db)):
    """Add reward points to a customer"""
    return controller.add_reward_points(
        db=db,
        customer_id=customer_id,
        points=points,
        reward_type=reward_type,
        order_id=order_id
    )


@router.post("/{customer_id}/rewards/redeem", response_model=schema.Customers)
def redeem_points(customer_id: int, points: int, db: Session = Depends(get_db)):
    """Redeem reward points"""
    return controller.redeem_reward_points(db=db, customer_id=customer_id, points_to_redeem=points)


@router.post("/{customer_id}/rewards/birthday", response_model=schema.Customers)
def award_birthday_reward(customer_id: int, db: Session = Depends(get_db)):
    """Award birthday reward"""
    return controller.check_birthday_reward(db=db, customer_id=customer_id)


