import uuid

from fastapi import FastAPI, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ResponseValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi_users import FastAPIUsers
from sqlalchemy.orm import Session

import crud
import schemas
from auth import auth_backend
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from database import get_async_session
from models import User

# models.Base.metadata.create_all(bind=engine)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title="Test App"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": exc.errors()})
    )


@app.get("/users/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: uuid.UUID, db: Session = Depends(get_async_session)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_async_session)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_async_session)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
