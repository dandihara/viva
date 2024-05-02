from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime

from models import Board
from dto.createBoradRequest import CreateBoardReqeustDto
from core.jwt import JWTAuth
from core.database import get_db
from repository.boardRepository import create, get_one, delete, get_list, update, add_view_count

board_router = APIRouter(
    prefix='/board',
    tags=['board']
)

@board_router.get('')
def search_board(id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == id).first()

    if board is None: 
        raise HTTPException(status_code = 411, detail = '존재하지 않는 게시글입니다')
    
    result = {
        'author' : board.user.name,
        'title': board.title,
        'content': board.content,
        'created_at': datetime.strftime(board.created_at, '%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.strftime(board.updated_at, '%Y-%m-%d %H:%M:%S') if board.updated_at is not None else "",
    }

    board.views = board.views + 1
    add_view_count(board, db)
    
    return JSONResponse(status_code=200, content=result)

@board_router.post('', dependencies=[Depends(JWTAuth())])
def create_board(ctx: CreateBoardReqeustDto, request: Request, db: Session = Depends(get_db)):
    if len(ctx.title) >= 100:
        raise HTTPException(status_code = 411, detail = '타이틀 길이가 맞지 않습니다.')
    
    board = Board(title = ctx.title, content = ctx.content, user_id = request.state.payload.id)
    create(board, db)
    return JSONResponse(status_code = 200, content = '게시글이 등록되었습니다')

@board_router.patch('', dependencies = [Depends(JWTAuth())])
def modify_board(id: int, user_id: int, change_values: dict, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == id).first()

    if board is None: 
        raise HTTPException(status_code = 411, detail = '존재하지 않는 게시글입니다')
    
    if board.user_id != user_id:
        return HTTPException(status_code = 400, detail = '권한이 없습니다.')
    
    
    change_permission_list = ['title', 'content']
    for key in change_values.keys():
        if key not in change_permission_list:
            raise HTTPException(
                status_code = 400, 
                detail = '본 항목은 변경이 불가합니다. Column : {}'.format(key)
                )
    change_values['updated_at'] = datetime.now()
    update(change_values, db)

    return JSONResponse(status_code = 200, content= '게시글이 변경되었습니다.')

@board_router.delete('', dependencies=[Depends(JWTAuth())])
def delete_board(id: int, request: Request, db: Session = Depends(get_db)):
    board = get_one(id, db)
    if board.user_id != request.state.payload.id:
        raise HTTPException(status_code = 411, detail = '삭제 권한이 없는 글입니다')
    
    delete(id,db)
    return JSONResponse(status_code = 200, content= '게시글이 삭제되었습니다.')

@board_router.get('/list')
def get_board_list(sort_type: str, page: int, db: Session = Depends(get_db)):
    sort_type_list  = ['views', 'created_at']
    if sort_type not in sort_type_list:
        raise HTTPException(status_code = 411, detail = '잘못된 파라미터입니다')
    
    board_list = get_list(sort_type, page, db)
    return board_list