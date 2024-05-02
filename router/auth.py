from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from dto.loginRequestDto import LoginRequestDto
from core.database import get_db
from models import User
from core.utils import get_hash_password
from core.jwt import create_access_token, create_refresh_token
from repository.userRepository import get_user_by_email

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@auth_router.post('')
def login(ctx: LoginRequestDto, db: Session = Depends(get_db)):
    user = get_user_by_email(ctx.email, db)

    if user is None:
        raise HTTPException(status_code = 400, detail = '존재하지 않는 이메일입니다.')

    hashed_password = get_hash_password(ctx.password)

    if user.password != hashed_password:
        raise HTTPException(status_code = 400, detail = '비밀번호가 일치하지 않습니다.')
    

    access_token = create_access_token({
            'email': user.email, 
            'id': user.id,
        })
    
    refresh_token = create_refresh_token({
            'email': user.email, 
            'id': user.id,
        })
    
    result = {
        'status_code': 200,
        'result' :{
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }
    return JSONResponse(status_code = 200, content = result)
