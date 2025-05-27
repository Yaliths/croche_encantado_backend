
import bcrypt
from dto import Login
from fastapi import HTTPException
from repository import (
    get_user_by_email
)



def login_user(login: Login, conn):
    user = get_user_by_email(conn, login.email)
    if user and bcrypt.checkpw(login.password.encode('utf-8'), user.password.encode('utf-8')):
        return {"message": "Login successful", "user": {"name": user.name, "email": user.email}}
    raise HTTPException(status_code=401, detail="Invalid email or password")