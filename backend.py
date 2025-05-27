import psycopg2
from dto import User
from fastapi import FastAPI, HTTPException
from repository import (create_user, get_all_users, edit_user, delete_user, get_user_by_email)
from auth import login_user
from dto import Login
import bcrypt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    conn = psycopg2.connect(
        "dbname='croche_encantado_bd' user='postgres' host='localhost' password='password'"
    )
except:
    print("I am unable to connect to the database")
print("Connected to the database")

cur = conn.cursor()

@app.get("/users", status_code=201)
def list_users():
    users = get_all_users(conn)
    return [
        {"name": user.name, "email": user.email, "password": user.password}
        for user in users
    ]

@app.get("/user/{email}", status_code=201)
def get_user(email: str):
    user = get_user_by_email(conn, email)
    if user:
        return {
            "name": user.name,
            "email": user.email,
            "password": user.password,
        }
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/create_user", status_code=201)
def create_new_user(user: User):
    existing_user = get_user_by_email(conn, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    create_user(user, conn)
    return {"message": "User created successfully"}


@app.put("/update_user/{email}", status_code=201)
def update_user(email: str, updates: dict):
    user = get_user_by_email(conn, email)
    if user:
        edit_user(updates, user, conn)
        return {"message": "User updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/delete_user/{id}", status_code=201)
def delete_user_by_id(id: int):
    user = get_user_by_email(conn, id)
    if user:
        delete_user(user, conn)
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/login", status_code=200)
def login(login: Login):
    return login_user(login, conn)