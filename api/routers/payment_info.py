from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import payment_info as controller
from ..schemas import payment_info as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=["Payment Info"],
    prefix="/payments",
)

@router.post("/", response_model=schema.PaymentInfo, status_code=status.HTTP_201_CREATED)
def create(request: schema.PaymentInfoCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)

@router.get("/", response_model=list[schema.PaymentInfo], status_code=status.HTTP_200_OK)
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)

@router.get("/{item_id}", response_model=schema.PaymentInfo)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db=db, item_id=item_id)

@router.put("/{item_id}", response_model=schema.PaymentInfo)
def update(item_id: int, request: schema.PaymentInfoUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)