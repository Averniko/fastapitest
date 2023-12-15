import uuid
from typing import List

from pydantic import BaseModel

from auth.schemas import UserRead


class ItemBase(BaseModel):
    title: str
    quantity: int


class ItemCreate(ItemBase):
    quantity: int = 0


class Item(ItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class ItemWithUsers(ItemBase):
    users: List[UserRead]
