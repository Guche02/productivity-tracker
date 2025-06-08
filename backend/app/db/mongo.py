from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")

client = AsyncIOMotorClient(MONGO_URI)
db = client["productivity_tracker"]

async def test_mongo_connection():
    try:
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except Exception as e:
        print("MongoDB connection failed:", e)

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())