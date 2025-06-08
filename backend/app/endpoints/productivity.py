from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user import ProductivityScore, ProductivityResponse
from db.mongo import db  
from core.auth import decode_token
from bson import ObjectId
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/users", tags=["users"])
auth_scheme = HTTPBearer()

users_collection = db["users"]
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials  
    try:
        # print(f"Received token: {token}")  
        payload = decode_token(token)
        user_id = payload.get("sub")
        # print(f"Decoded user ID: {user_id}")  
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post("/productivity", response_model=ProductivityResponse, status_code=200)
async def update_productivity(
    productivity: ProductivityScore,
    current_user: dict = Depends(get_current_user)         # depends is used to get the current user from the token, and if not found the route doesn't proceed.
):
    for field, value in productivity.dict().items():
        if value < 0 or value > 5:
            raise HTTPException(
                status_code=400,
                detail=f"{field} score must be between 0 and 5"
            )

    overall = round(sum(productivity.dict().values()) / 5, 2)

    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "productivity": productivity.dict(),
            "overall_productivity": overall
        }}
    )

    return {
        "message": "Productivity updated successfully",
        "overall_score": overall,
        "details": productivity.dict()
    }