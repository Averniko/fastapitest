import uuid

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(CreateUpdateDictModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str
