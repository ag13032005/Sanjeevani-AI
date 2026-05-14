from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_database
from app.schemas import TokenResponse, UserCreate, UserLogin

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: UserCreate, db=Depends(get_database)):
    existing_user = await db.users.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_doc = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    access_token = create_access_token(str(result.inserted_id))
    return TokenResponse(
        access_token=access_token,
        user_id=str(result.inserted_id),
        name=user_doc["name"],
        email=user_doc["email"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db=Depends(get_database)):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user["_id"]))
    return TokenResponse(
        access_token=access_token,
        user_id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
    )
