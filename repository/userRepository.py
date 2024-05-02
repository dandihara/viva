from sqlalchemy.orm import Session
from pydantic import EmailStr

from models import User

def get_user_by_email(email: EmailStr, db: Session):
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user

def get_user_by_id(id: int, db: Session):
    user = db.query(User).filter(User.id == id).first()
    db.close()
    return user

def insert_user(new_user: User, db: Session):
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

def resign_user(out_user: User, db: Session):
    db.add(out_user)
    db.commit()
    db.close()

def update_user(update_ctx: dict, email: EmailStr, db: Session):
    db.query(User).filter(User.email == email).update(update_ctx)
    db.commit()
    db.close()