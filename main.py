import uuid

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from auth.auth import auth_backend
from auth.auth import current_active_user, fastapi_users
from auth.schemas import UserRead, UserCreate, UserUpdate
from database import get_async_session, get_user_db
from models import User

app = FastAPI(
    title="Test App"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


# @app.exception_handler(ResponseValidationError)
# async def validation_exception_handler(request: Request, exc: ResponseValidationError):
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content=jsonable_encoder({"detail": exc.errors()})
#     )


@app.get("/users/", response_model=list[UserRead])
async def read_users(skip: int = 0, limit: int = 100, user_db: crud.UserDatabase = Depends(get_user_db),
                     user: User = Depends(current_active_user)):
    users = await user_db.get_users(skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: uuid.UUID, user_db: crud.UserDatabase = Depends(get_user_db),
                    user: User = Depends(current_active_user)):
    db_user = user_db.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.ItemWithUsers)
async def create_item_for_user(
        user_id: uuid.UUID, item: schemas.ItemCreate, user_db: crud.UserDatabase = Depends(get_user_db),
        user: User = Depends(current_active_user)
):
    return await user_db.create_user_item(item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session),
               user: User = Depends(current_active_user)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
