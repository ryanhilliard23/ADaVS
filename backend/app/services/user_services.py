import os
import pyseto
import json
from pyseto import Key
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..models import user as user_model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

PASETO_KEY = Key.new(
    version=4,
    purpose="local",
    key=bytes.fromhex(os.getenv("SECRET_KEY"))
)

class User(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = user_model.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(user: User):
    expiration_time = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        'sub': user.email,
        'user_id': user.id,
        'exp': expiration_time.isoformat()
    }
    token = pyseto.encode(
        key=PASETO_KEY,
        payload=payload,
        footer={'kid': 'v4.local.key'},
    )
    return token.decode('utf-8')

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = pyseto.decode(PASETO_KEY, token)
        payload_bytes = decoded_token.payload
        
        payload = json.loads(payload_bytes)

        user_id = payload.get('user_id')
        email = payload.get('sub')

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return {"user_id": int(user_id), "email": email}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )