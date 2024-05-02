from pydantic import BaseModel, EmailStr

class RegisterUserRequestDto(BaseModel):
    name: str
    email: EmailStr
    password: str
                                                 