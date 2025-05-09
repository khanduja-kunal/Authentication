# app/api/v1/user/schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi import UploadFile, File, Form

# RESPONSE SCHEMA
class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile_picture_url: Optional[str] = None

    class Config:
        orm_mode = True

# FOR PATCH REQUEST (multipart/form-data with file support)
class UserProfileUpdateMultipart:
    def __init__(
        self,
        name: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None),
    ):
        self.name = name
        self.file = file