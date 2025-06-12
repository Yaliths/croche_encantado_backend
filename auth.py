import jwt
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import bcrypt
from dto import Login, User
from fastapi import HTTPException
from repository import (
    get_user_by_email,
    create_user
)
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRATION_TIME = 3600  # 1 hour

def access_token(email: str):
    payload = {"email": email}
    payload["exp"] = datetime.utcnow() + timedelta(seconds=EXPIRATION_TIME)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def is_token_expired(token: str):
    try:
        # Isso já verifica a expiração automaticamente
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return False  # Token válido
    except jwt.ExpiredSignatureError:
        return True  # Token expirou
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def login_user(login: Login, conn):
    user = get_user_by_email(conn, login.email)
    if user and bcrypt.checkpw(login.password.encode('utf-8'), user.password.encode('utf-8')):
        token = access_token(user.email)
        print(f"Token generated: {token}")
        return {"message": "Login successful", "user": {"name": user.name, "email": user.email, "access_token": token}}
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

def register_user(user: User, conn):
    existing_user = get_user_by_email(conn, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    create_user(user, conn)
    token = generate_verification_token(user.email)
    send_verification_email(user.email, token)
    return {"message": "User created successfully. Check your email to verify your account."}

def generate_verification_token(email: str):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # expira em 24h
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def send_verification_email(email: str, token: str):
    verification_link = f"http://localhost:8000/verify_email?token={token}"
    msg = MIMEText(f"Clique no link para verificar seu e-mail: {verification_link}")
    msg['Subject'] = 'Verifique seu e-mail'
    msg['From'] = 'crocheencantado.magic@gmail.com'
    msg['To'] = email

    # Exemplo com Gmail (ative "apps menos seguros" na conta para testes)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('crocheencantado.magic@gmail.com', 'senha')
        server.send_message(msg)


def verify_email(token: str, conn):
    if not token:
        raise HTTPException(status_code=400, detail="Token não fornecido")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]
        # Aqui, marque o usuário como verificado no banco de dados
        # Exemplo: set_user_verified(conn, email)
        return {"message": "E-mail verificado com sucesso!"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido")