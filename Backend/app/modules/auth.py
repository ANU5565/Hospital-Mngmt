thon
from datetime import timedelta
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session

from .database import get_db
from .models import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_email_password(username: str, password: str):
    user = User.get_or_none(email=username)
    
    if not user or not user.password == password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

class TokenData:
    def __init__(self, email=None, role_id=None):
        self.email = email
        self.role_id = role_id

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "JWT_SECRET_KEY", algorithm="HS256")
    return encoded_jwt

def authenticate_user(username: str, password: str):
    user = User.get_or_none(email=username)
    
    if not user or not user.password == password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = TokenData.from_string(token)
    verify_email_password(username=token_data.email, password=token_data.password)
    
    user = User.get_or_none(email=token_data.email)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    role_id = Role.filter_by(name=user.role.name).first().id
    return {"email": token_data.email, "role_id": role_id}

async def get_current_active_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user