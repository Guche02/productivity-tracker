from fastapi import APIRouter, HTTPException, status
from schemas.user import UserBase, UserOut, UserLogin, Token
from db.mongo import db
from core.auth import create_access_token
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]

@router.post("/create", response_model=UserOut)
async def create_user(user: UserBase):
    
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()

    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})

    return UserOut(
        id=str(created_user["_id"]),
        email=created_user["email"],
        created_at=created_user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    existing_user = await users_collection.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {"sub": str(existing_user["_id"]), "email": existing_user["email"]}
    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}