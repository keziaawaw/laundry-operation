from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.jwt_handler import create_token
from auth.models import UserRegister, UserResponse
from auth.password import hash_password, verify_password
from auth.repository import user_repository

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    try:
        hashed_password = hash_password(user_data.password)
        user = user_repository.create_user(
            username=user_data.username, email=user_data.email, hashed_password=hashed_password, full_name=user_data.full_name
        )
        return UserResponse(
            id=user.id, username=user.username, email=user.email, full_name=user.full_name, created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating user: {str(e)}")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_repository.get_user_by_username(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = create_token({"sub": user.username, "user_id": user.id})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating token: {str(e)}")
