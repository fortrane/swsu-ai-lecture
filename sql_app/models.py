from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Logger(Base):
    __tablename__ = "loggers"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    upload_date = Column(DateTime, default=func.now())
    file_size = Column(Integer)


class FileData(Base):
    __tablename__ = "file_data"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    test = Column(Text, nullable=True)
    test_raw = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    summary_time = Column(Integer, nullable=True)
    qa_time = Column(Integer, nullable=True)

    file = relationship("File", back_populates="data")


File.data = relationship("FileData", order_by=FileData.id, back_populates="file")
