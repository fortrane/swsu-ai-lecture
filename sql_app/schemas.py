from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class FileBase(BaseModel):
    filename: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    upload_date: datetime

    class Config:
        orm_mode = True


class FileDataBase(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    test: Optional[str] = None
    test_raw: Optional[str] = None


class FileDataCreate(FileDataBase):
    file_id: int


class FileDataUpdate(FileDataBase):
    pass


class FileData(FileDataBase):
    id: int
    file_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FileResponse(BaseModel):
    filename: str
    id: int


class FileInfo(BaseModel):
    id: int
    filename: str
    upload_date: datetime

    class Config:
        orm_mode = True


class FileDataDetail(BaseModel):
    id: int
    file_id: int
    content: Optional[str] = None
    summary: Optional[str] = None
    test: Optional[str] = None
    test_raw: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FileDataResponse(BaseModel):
    file: FileInfo
    data: FileDataDetail
