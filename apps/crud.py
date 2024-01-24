import uuid
from typing import Optional, List
from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select, func, or_, Select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from models import User


class UserDatabase(SQLAlchemyUserDatabase):
    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(self.user_table).where(
            or_(
                func.lower(self.user_table.email) == func.lower(email),
                func.lower(self.user_table.username) == func.lower(email),
            )
        )
        return await self._get_user(statement)

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(self.user_table).order_by(self.user_table.id.desc()).offset(skip).limit(limit)
        return await self._get_users(statement)

    async def create_user_item(self, item: schemas.ItemCreate, user_id: uuid.UUID):
        db_item = models.Item(**item.model_dump())
        db_user = await self.get_user_by_id(user_id=user_id)
        db_item.users.append(db_user)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item, ["users"])
        return db_item

    async def _get_users(self, statement: Select) -> List[User]:
        results = await self.session.execute(statement)
        return results.unique().scalars()


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()
