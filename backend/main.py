from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.users import router as users_router
from app.endpoints.productivity import router as productivity_router
from app.services.whatsapp_agent import start_scheduler
import uvicorn

app = FastAPI()

# CORS setup for Streamlit access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(productivity_router)

start_scheduler()

if  __name__ == "__main__":
     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)