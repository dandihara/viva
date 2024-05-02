from sqlalchemy.orm import Session
from datetime import datetime

from models import Board

def create(board: Board, db: Session):
    db.add(board)
    db.commit()
    db.close()

def get_one(id: int, db: Session):
    board = db.query(Board).filter(Board.id == id).first()
    db.close()
    return board

def delete(id: int, db: Session):
    db.query(Board).filter(Board.id == id).delete()
    db.commit()
    db.close()

def get_list(sort_type: str, page:int, db: Session):
    if sort_type == 'views':
        board_list = db.query(Board).order_by(Board.views.desc()).offset((page-1) * 2).limit(page * 2).all()
    elif sort_type == 'created_at':
        board_list = db.query(Board).order_by(Board.created_at.desc()).offset((page-1) * 2).limit(page * 2).all()
        conveting_list = []

    for board in board_list:
        result = {
            'author' : board.user.name if board.user.deleted_at is None else "탈퇴한 유저",
            'title': board.title,
            'content': board.content,
            'created_at': datetime.strftime(board.created_at, '%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.strftime(board.updated_at, '%Y-%m-%d %H:%M:%S') if board.updated_at is not None else "",
        }
        conveting_list.append(result)

    return board_list

def add_view_count(board: Board, db: Session):
    db.add(board)
    db.commit()
    db.close()

def update(change_values: dict, db: Session):
    db.query(Board).filter(Board.id == id).update(change_values)
    db.commit()
    db.close()