from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    upload_date = Column(DateTime, default=func.now())

class FileData(Base):
    __tablename__ = "file_data"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    content = Column(Text, nullable=True)  # Для хранения большого объема текста
    summary = Column(Text, nullable=True)
    test = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    file = relationship("File", back_populates="data")

File.data = relationship("FileData", order_by=FileData.id, back_populates="file")
