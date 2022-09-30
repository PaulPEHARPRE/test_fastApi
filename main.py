import base64
from typing import Union

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse, RedirectResponse, Response

from authentication_methods import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                    authenticate_user, create_access_token,
                                    get_current_active_user, timedelta)
from basic_auth_class import BasicAuth, basic_auth
from fake_db import fake_users_db
from models import Token, User, UserLogin

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/")
def root(auth: BasicAuth = Depends(basic_auth)):
    print(auth)
    return "server up and running..."

@app.get("/openapi.json")
async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
    return JSONResponse(get_openapi(title="FastAPI", version=1, routes=app.routes))


@app.get("/docs")
async def get_documentation(current_user: User = Depends(get_current_active_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

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

@app.get("/login_basic")
async def login_basic(auth: BasicAuth = Depends(basic_auth)):
    print(auth)
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response
    try:
        decoded = base64.b64decode(auth).decode("ascii")
        username, _, password = decoded.partition(":")
        if username == "" and password == "":
            response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
            return response
        user = authenticate_user(fake_users_db, username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        token = jsonable_encoder(access_token)
        
        response = RedirectResponse(url="/docs")
        response.set_cookie(
            "Authorization",
            value=f"Bearer {token}",
            domain="localhost",
            httponly=True,
            max_age=1800,
            expires=1800,
        )
        return response

    except:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

@app.post("/login_api")
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


@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/", headers={"WWW-Authenticate": "Basic"})
    response.delete_cookie("Authorization", domain="localhost")
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# reminder not to use reload in production (too many rerenders)
