from typing import Union
from fastapi import Depends, FastAPI
from models import User
from authentication_methods import get_current_user
import uvicorn

app = FastAPI()

@app.get("/api/")
def root():
    return "server up and running..."

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# reminder not to use reload in production (too many rerenders)