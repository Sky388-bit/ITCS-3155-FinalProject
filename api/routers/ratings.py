from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import ratings as controller
from ..schemas import ratings as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Ratings'],
    prefix="/ratings"
)


@router.get("/", response_model=list[schema.Ratings])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Ratings)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Ratings)
def update(item_id: int, request: schema.Ratings, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
