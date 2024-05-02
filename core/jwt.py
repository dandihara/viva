from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
from jose import JWTError, jwt
from zoneinfo import ZoneInfo
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader, HTTPBearer
from sqlalchemy.orm import Session

from repository.userRepository import get_user_by_id
from core.database import get_db

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
)

expired_exception =  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token Is Expired",
)

none_exception =  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User Not Found",
)


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_TIME = int(os.getenv('ACCESS_TOKEN_EXPIRE_TIME'))
REFRESH_TOKEN_EXPIRE_TIME = int(os.getenv('REFRESH_TOKEN_EXPIRE_TIME'))
jwt_header = APIKeyHeader(name = 'Authorization')

def check_token_expired(token: str) -> dict | None:
    payload = decode_token(token)

    now = datetime.timestamp(datetime.now(ZoneInfo('UTC')))

    if payload and payload['exp'] < now:
        return None
    
    return payload

def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)
    payload = {
        'sub': data,
        'exp': expire.strftime('%Y-%m-%d %H:%M:%S') 
    }     
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return access_token

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes = REFRESH_TOKEN_EXPIRE_TIME)
    payload = {
        'sub': data,
        'exp': expire.strftime('%Y-%m-%d %H:%M:%S') 
    }     
    refresh_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return refresh_token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print(payload)
        user_id = payload.get('user_id')
        
        if user_id is None:
            raise credentials_exception
    
        return payload
    except:
        raise HTTPException(status_code = 401, detail = '정상적인 Token이 아닙니다.')
        
async def jwt_guard(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get('Authorization')
    if token is None:
        raise credentials_exception

    payload = decode_token(token)
    user_id = payload.get('id')

    user = get_user_by_id(user_id, db)
    if user is None:
        raise none_exception
    
    return payload

class JWTAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTAuth, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise credentials_exception
        token_type, token = auth_header.split(' ')
      
        if token_type != 'Bearer':
            raise HTTPException(400, detail='Invaild Token Type')
        
        try:
            request.state.payload = decode_token(token)
        except Exception as e:
            print(e)
            raise HTTPException(400, detail='Invaild Token')

