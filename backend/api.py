from fastapi import FastAPI
from pydantic import BaseModel
from backend.auth import register_user, login_user

app = FastAPI()


class User(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(user: User):
    return register_user(user.username, user.email, user.password)


@app.post("/login")
def login(data: Login):
    return login_user(data.username, data.password)