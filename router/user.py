from dto.registerRequestDto import RegisterUserRequestDto
from fastapi import APIRouter, HTTPException, Depends, Request
import re
from pydantic import EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import JSONResponse

from core.jwt import JWTAuth
from models import User
from dto.registerRequestDto import RegisterUserRequestDto
from core.database import get_db
from core.utils import get_hash_password
from repository.userRepository import get_user_by_email, insert_user, resign_user, update_user, get_user_by_id

user_router = APIRouter(
    prefix='/user',
    tags=['user']
)

def _check_password(password: str):
    if not re.match(r'^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        raise HTTPException(status_code=400, detail='비밀번호 패턴 불일치')

@user_router.post('/register')
def register(ctx: RegisterUserRequestDto, db: Session = Depends(get_db)):
    _check_password(ctx.password)
    
    hashed_password = get_hash_password(ctx.password)
    
    insert_user(
        User(email = ctx.email, password = hashed_password, name = ctx.name), db
    )

    return JSONResponse({'status_code': 200, 'result': {'msg': '정상적으로 회원 가입 되었습니다.'}})

@user_router.get('')
def search_user(email: EmailStr, db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=400, detail = '가입한 이력이 없습니다.')

    return JSONResponse(status_code = 200, content = {'id': user.id, 'email': user.email, 'registed_at': datetime.strftime(user.registed_at, '%Y-%m-%d %H:%M:%S')})

@user_router.patch('/delete', dependencies=[Depends(JWTAuth())])
def delete_user(request: Request, db: Session = Depends(get_db)):
    user = get_user_by_id(request.state.payload.id, db)

    if user.deleted_at is not None:
        raise HTTPException(status_code = 400, detail = '이미 탈퇴한 회원입니다.')
    
    user.deleted_at = datetime.now()

    resign_user(user, db)

    return JSONResponse(status_code =  200, content =  {'msg': '탈퇴 완료되었습니다.'})

@user_router.patch('/update', dependencies=[Depends(JWTAuth())])
def modify_user(
        password: str, 
        change_values:dict, 
        request: Request,
        db: Session = Depends(get_db)
    ):
    request_user = get_user_by_email(request.state.payload.email, db)
    if get_hash_password(password) != request_user.password:
        raise HTTPException(status_code = 400, detail = '기존 비밀번호가 불일치합니다.')
    
    update_data = {}
    change_permission_list = ['password', 'name']

    for key in change_values.keys():
        if key not in change_permission_list:
            raise HTTPException(
                status_code = 400, 
                detail = '본 항목은 변경이 불가합니다. Column : {}'.format(key)
                )
            
        if key == 'password':
            _check_password(change_values['password'])
            update_data['password'] = get_hash_password(change_values['password'])

        if key == 'name':
            update_data['name'] = change_values['name']

    update_user(update_data, db)

    return JSONResponse(status_code = 200,content= {'msg': '유저 정보가 업데이트 되었습니다.'})
