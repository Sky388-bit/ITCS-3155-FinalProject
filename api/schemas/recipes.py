from typing import Optional
from pydantic import BaseModel, ConfigDict
from .resources import Resource
from .menu import Menu


class RecipeBase(BaseModel):
    amount: int


class RecipeCreate(RecipeBase):
    menu_id: int
    resource_id: int

class RecipeUpdate(BaseModel):
    menu_id: Optional[int] = None
    resource_id: Optional[int] = None
    amount: Optional[int] = None

class Recipe(RecipeBase):
    id: int
    menu_id: int
    resource_id: int
    menu: Optional[Menu] = None
    resource: Optional[Resource] = None

    model_config = ConfigDict(from_attributes=True)