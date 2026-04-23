from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from db.dals.user_dal import UserDAL
from dependencies import get_user_dal
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    user_dal: UserDAL = Depends(get_user_dal),
):
    return await user_dal.create_user(payload.name, payload.email, payload.mobile)


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    user_dal: UserDAL = Depends(get_user_dal),
):
    user = await user_dal.update_user(
        user_id, payload.name, payload.email, payload.mobile
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    user_dal: UserDAL = Depends(get_user_dal),
):
    user = await user_dal.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


@router.get("/users", response_model=List[UserRead])
async def get_all_users(user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.get_all_users()