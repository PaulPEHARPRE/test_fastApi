import base64
from typing import Union

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse, RedirectResponse, Response
from config import config_env
from authentication_methods import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                    authenticate_user, create_access_token,
                                    get_current_active_user, timedelta)
from fake_db import fake_users_db
from models import Token, User, UserLogin

app = FastAPI()

@app.get("/")
def root():
    return "server up and running..."

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/login")
async def login_basic(data: UserLogin):
    try:
        user = authenticate_user(fake_users_db, data.username, data.password)
        if not user:
            raise HTTPException(status_code=404, detail="Incorrect email or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": data.username}, expires_delta=access_token_expires
        )

        token = jsonable_encoder(access_token)
        print(type(user.__dict__))
        print(type({"message": "Come to the dark side, we have cookies"}))
        response = JSONResponse(content = user.__dict__)
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {token}",
            httponly=True,
            max_age=1800,
            expires=1800,
        )
        return response
    except:
        raise HTTPException(status_code=400, detail="Bad Request")


@app.post("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("Authorization", domain=config_env["HOST"])
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host=config_env["HOST"], port=8000, reload=True)

# reminder not to use reload in production (too many rerenders)
