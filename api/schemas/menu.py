from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MenuBase(BaseModel):
    dish_name: str
    dish_description: str
    price: Decimal
    calories: int
    category: str

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    dish_name: Optional[str]
    dish_description: Optional[str]
    price: Optional[Decimal]
    calories: Optional[int]
    category: Optional[str]

class Menu(MenuBase):
    id: int

    model_config = ConfigDict(from_attributes=True)