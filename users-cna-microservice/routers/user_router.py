from typing import List

from fastapi import APIRouter, Depends

from db.dals.user_dal import UserDAL
from dependencies import get_user_dal
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("/users")
async def create_user(payload: UserCreate, user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.create_user(payload.name, payload.email, payload.mobile)


@router.put("/users/{user_id}")
async def update_user(user_id: int, payload: UserUpdate, user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.update_user(user_id, payload.name, payload.email, payload.mobile)


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.get_user(user_id)


@router.get("/users", response_model=List[UserRead])
async def get_all_users(user_dal: UserDAL = Depends(get_user_dal)):
    return await user_dal.get_all_users()