from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import ProductivityScore, ProductivityResponse
from app.db.mongo import db  
from app.core.auth import decode_token
from app.services.chatbot import chatbot
from bson import ObjectId
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

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
    user_input: str,
    current_user: dict = Depends(get_current_user)
):
    thread_id = str(current_user["_id"])
    productivity = chatbot(user_input, thread_id=thread_id)
    print("Productivity received:")

    if productivity["scores"]:
        scores = productivity["scores"]

        for field, value in scores.items():
            if value < 0 or value > 5:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field} score must be between 0 and 5"
                )

        overall = round(sum(scores.values()) / len(scores), 2)
        today = datetime.utcnow().date().isoformat()

        today_entry = {
            "date": today,
            **scores,
            "overall": overall
        }

        update_result = await users_collection.update_one(
            {
                "_id": current_user["_id"],
                "productivity.date": today
            },
            {
                "$set": {
                    "productivity.$.exercise": scores.get("exercise", 0),
                    "productivity.$.study": scores.get("study", 0),
                    "productivity.$.meditation": scores.get("meditation", 0),
                    "productivity.$.hobby": scores.get("hobby", 0),
                    "productivity.$.rest_time": scores.get("rest_time", 0),
                    "productivity.$.overall": overall
                }
            }
        )
        if update_result.modified_count == 0:
            await users_collection.update_one(
                {"_id": current_user["_id"]},
                {"$push": {"productivity": today_entry}}
            )

        return {
            "message": productivity["result"],
            **scores,
            "overall": overall
        }

    return {
        "message": productivity["result"]
    }

# returns the productivity history
@router.get("/productivity-history")
async def get_productivity_history(current_user: dict = Depends(get_current_user)):
    productivity = current_user.get("productivity", [])
    last_7_days = sorted(productivity, key=lambda x: x["date"], reverse=True)[:7]
    return list(reversed(last_7_days))  


@router.post("/add-dummy-scores")
async def add_dummy_scores(current_user: dict = Depends(get_current_user)):
    from random import uniform
    from datetime import timedelta

    dummy_scores = []
    for i in range(7):
        d = datetime.utcnow().date() - timedelta(days=i)

        exercise = round(uniform(1, 5), 1)
        study = round(uniform(1, 5), 1)
        meditation = round(uniform(1, 5), 1)
        hobby = round(uniform(1, 5), 1)
        rest_time = round(uniform(1, 5), 1)

        overall = round(
            (exercise + study + meditation + hobby + rest_time) / 5, 2
        )
        scores = {
            "date": d.isoformat(),
            "exercise": exercise,
            "study": study,
            "meditation": meditation,
            "hobby": hobby,
            "rest_time": rest_time,
            "overall": overall
        }
        dummy_scores.append(scores)

    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$push": {"productivity": {"$each": dummy_scores}}}
    )
    return {"message": "Dummy productivity scores added"}