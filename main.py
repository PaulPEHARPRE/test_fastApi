import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse, RedirectResponse
from config import config_env
from src.authentication_methods import (ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token,
                                    get_current_user_email, get_password_hash, timedelta, verify_password)
from src.models import Token, User, UserLogin, UserPostgress, UserInDB
from src.schemas import CreateUserRequest
from sqlalchemy.orm import Session
from src.database import get_db

app = FastAPI()

@app.get("/")
def root():
    return "server up and running..."

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    userDBObject = db.query(UserPostgress).filter(UserPostgress.email == form_data.username).first()
    if not userDBObject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    userDB = userDBObject.__dict__
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": userDB["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user_email: User = Depends(get_current_user_email), db: Session = Depends(get_db)):
    userDBObject = db.query(UserPostgress).filter(UserPostgress.email == current_user_email).first()
    return {"email": userDBObject.__dict__["email"]}

@app.post("/login")
async def login_basic(data: UserLogin, db: Session = Depends(get_db)):
    try:
        userDBObject = db.query(UserPostgress).filter(UserPostgress.email == data.email).first() 
        if not userDBObject:
            raise HTTPException(status_code=404, detail="Incorrect email")
        userDB = userDBObject.__dict__
        if not verify_password(data.password, userDB["password"]):
            raise HTTPException(status_code=404, detail="Incorrect password")        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": data.email}, expires_delta=access_token_expires
        )
        print('test au ch')
        token = jsonable_encoder(access_token)
        response = JSONResponse(content = {"email": userDB["email"]})
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


@app.post("/create_user")
def create(details: CreateUserRequest, db: Session = Depends(get_db)):
    userDBObject = db.query(UserPostgress).filter(UserPostgress.email == details.email).first() 
    if userDBObject:
        raise HTTPException(status_code=404, detail="Email already exists")
    hashedPassword = get_password_hash(details.password)
    to_create = UserPostgress(
        email=details.email,
        password=hashedPassword
    )
    db.add(to_create)
    db.commit()
    return { 
        "success": True,
        "created_id": to_create.id
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=config_env["HOST"], port=8000, reload=True)

# reminder not to use reload in production (too many rerenders)
