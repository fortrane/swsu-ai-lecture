import os

import llm_part
import document_loaders as dl
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
import utility_part
from sql_app import models, schemas
from sqlalchemy.orm import Session
from sql_app.database import SessionLocal
from datetime import datetime
from sql_app.database import engine
import docx2txt
from PyPDF2 import PdfReader

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def summary(file_name):
    if file_name.split('.')[1] == 'pdf':
        return llm_part.summary(dl.pdf_loader(file_name))
    elif file_name.split('.')[1] == 'docx':
        return llm_part.summary(dl.docx_loader(file_name))
    else:
        return 'Файл неправильно назван(name.pdf) или имеет не верный формат pdf/docx'


def qa(file_name):
    if file_name.split('.')[1] == 'pdf':
        return llm_part.qa_json_bilder_PDF(llm_part.qa_generation(dl.pdf_loader(file_name)))
    elif file_name.split('.')[1] in ['docx', 'doc']:
        return llm_part.qa_json_bilder_DOCX(llm_part.qa_generation(dl.docx_loader(file_name)))
    else:
        return 'Файл неправильно назван(name.pdf) или имеет не верный формат pdf/docx'


# starting web application
app = FastAPI()


@app.post("/upload-file", response_model=schemas.FileResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_name = utility_part.generate_random_filename(file.filename)
        file_path = os.path.join(os.getcwd(), "temp", file_name)
        contents = file.file.read()

        with open(file_path, 'wb') as f:
            f.write(contents)

        # Определение контента файла в зависимости от его типа
        if file.filename.endswith('.pdf'):
            reader = PdfReader(file_path)
            content = " ".join([page.extract_text() for page in reader.pages if page.extract_text() is not None])
        elif file.filename.endswith('.docx'):
            content = docx2txt.process(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Создание записи в таблице files и file_data
        db_file = models.File(filename=file_name, upload_date=datetime.utcnow())
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        db_file_data = models.FileData(
            file_id=db_file.id,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_file_data)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

    return {"filename": file_name, "id": db_file.id}


@app.post("/process-summary/{file_data_id}")
def process_summary(file_data_id: int, db: Session = Depends(get_db)):
    # Находим запись в таблице file_data по ID
    db_file_data = db.query(models.FileData).filter(models.FileData.id == file_data_id).first()
    if not db_file_data:
        raise HTTPException(status_code=404, detail="FileData not found")

    # Находим связанный файл, чтобы получить его имя и путь
    db_file = db.query(models.File).filter(models.File.id == db_file_data.file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(os.getcwd(), "temp", db_file.filename)

    # Вызываем функцию summary, передавая путь файла
    summary_text = summary(file_path)

    # Обновляем запись в базе данных с результатом summary
    db_file_data.summary = summary_text
    db.commit()


@app.post("/process-qa/{file_data_id}")
def process_qa(file_data_id: int, db: Session = Depends(get_db)):
    # Повторяем те же шаги, что и в эндпоинте для summary
    db_file_data = db.query(models.FileData).filter(models.FileData.id == file_data_id).first()
    if not db_file_data:
        raise HTTPException(status_code=404, detail="FileData not found")

    db_file = db.query(models.File).filter(models.File.id == db_file_data.file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(os.getcwd(), "temp", db_file.filename)

    # Вызываем функцию qa, передавая путь файла
    qa_text = qa(file_path)
    qa_text_corrected = utility_part.correct_qa_format(qa_text)

    # Обновляем запись в базе данных с результатом qa
    db_file_data.test = qa_text_corrected
    db.commit()


@app.get("/file/{file_id}", response_model=schemas.FileDataResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    db_file_data = db.query(models.FileData).filter(models.FileData.file_id == file_id).first()
    if db_file_data is None:
        raise HTTPException(status_code=404, detail="File data not found")

    # Создаем ответ используя модели Pydantic
    file_info = schemas.FileInfo.from_orm(db_file)
    file_data_detail = schemas.FileDataDetail.from_orm(db_file_data)
    response = schemas.FileDataResponse(file=file_info, data=file_data_detail)

    return response


@app.delete("/file/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()
    return {"message": "File and associated data deleted"}
