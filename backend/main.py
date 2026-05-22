from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
(revised)
from backend.database import engine, Base, get_db
from backend import models
from backend.schemas import UserRegister, UserLogin
from backend.services.auth_services import register_user, login_user

app = FastAPI()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user.username, user.email, user.password)


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.username, user.password)
