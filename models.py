from sqlalchemy import Column, String, Integer, TEXT, ForeignKey, DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship
from core.database import Base

class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(TEXT)
    views = Column(Integer, default = 0)
    created_at = Column(DateTime(timezone=True), nullable=False, default = func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref = 'owner', foreign_keys=[user_id])

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    registed_at = Column(DateTime(timezone=True), nullable=False, default = func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

