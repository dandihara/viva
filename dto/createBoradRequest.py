from pydantic import BaseModel

class CreateBoardReqeustDto(BaseModel):
    title: str
    content: str
