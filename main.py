from fastapi import FastAPI, Request, HTTPException

import models
from core.database import engine
from core.jwt import check_token_expired
from router.user import user_router
from router.auth import auth_router
from router.board import board_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(board_router)
