from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResourceBase(BaseModel):
    item: str
    amount: int
    min_threshold: int


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    item: Optional[str] = None
    amount: Optional[int] = None
    min_threshold: Optional[int] = None


class Resource(ResourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
