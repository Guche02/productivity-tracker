from fastapi import FastAPI
from endpoints.users import router as users_router
from endpoints.productivity import router as productivity_router

import uvicorn

app = FastAPI()
app.include_router(users_router)
app.include_router(productivity_router)

if  __name__ == "__main__":
     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)