import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Integer, String, Column, ForeignKey, Table, UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


item_user_association = Table(
    "item_user",
    Base.metadata,
    Column("id", UUID, primary_key=True, index=True, default=uuid.uuid4),
    Column("item_id", UUID, ForeignKey("item.id")),
    Column("user_id", UUID, ForeignKey("user.id"))
)


class User(SQLAlchemyBaseUserTableUUID, Base):
    username = Column(String, nullable=False)
    items = relationship("Item", secondary=item_user_association, back_populates="users", lazy="joinedload")


class Item(Base):
    __tablename__ = "item"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    users = relationship("User", secondary=item_user_association, back_populates="items", lazy="joinedload")
