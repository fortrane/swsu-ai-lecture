import json
import os
import time
import nltk
import llm_part
import document_loaders as dl
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sql_app import models, schemas
from sqlalchemy.orm import Session
from sql_app.database import SessionLocal
from datetime import datetime
from sql_app.database import engine
import docx2txt
from PyPDF2 import PdfReader
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def summary(file_name, facts_num=10):
    if file_name.split('.')[1] == 'pdf':
        return "Временно недоступно загружать документы формата PDF."
    elif file_name.split('.')[1] == 'docx':
        return llm_part.summary(dl.docx_loader(file_name), facts_num=7)
    else:
        return 'Файл неправильно назван(name.pdf) или имеет не верный формат pdf/docx'


def qa(file_name):
    if file_name.split('.')[1] == 'pdf':
        return "Временно недоступно загружать документы формата PDF."
    elif file_name.split('.')[1] in ['docx', 'doc']:
        return llm_part.smaller_qa(dl.docx_loader(file_name))
    else:
        return 'Файл неправильно назван(name.pdf) или имеет не верный формат pdf/docx'


# starting web application
app = FastAPI()
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-file", response_model=schemas.FileResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # file_name = utility_part.generate_random_filename(file.filename)
        file_name = file.filename
        file_path = os.path.join(os.getcwd(), "temp", file_name)
        contents = file.file.read()

        with open(file_path, 'wb') as f:
            f.write(contents)

        file_size = os.path.getsize(file_path)

        # Определение контента файла в зависимости от его типа
        if file.filename.endswith('.pdf'):
            reader = PdfReader(file_path)
            content = " ".join([page.extract_text() for page in reader.pages if page.extract_text() is not None])
        elif file.filename.endswith('.docx'):
            content = docx2txt.process(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Создание записи в таблице files и file_data
        db_file = models.File(filename=file_name, upload_date=datetime.utcnow(), file_size=file_size)
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
    start_time = time.time()
    summary_text = summary(file_path)
    end_time = time.time()
    execution_time = end_time - start_time
    # print(execution_time)
    if isinstance(summary_text, dict) and summary_text.get("status_code") == 401:
        raise HTTPException(status_code=401, detail="Blacklisted chunk: " + str(summary_text.get("Blacklisted chunk")))

    # Обновляем запись в базе данных с результатом summary
    db_file_data.summary = summary_text
    db_file_data.summary_time = int(execution_time)
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
    start_time = time.time()
    qa_text = qa(file_path)
    end_time = time.time()
    execution_time = end_time - start_time
    qa_text_json = json.dumps(qa_text, ensure_ascii=False, indent=None)
    if isinstance(qa_text, dict) and qa_text.get("status_code") == 401:
        raise HTTPException(status_code=401, detail="Blacklisted chunk: " + str(qa_text.get("Blacklisted chunk")))

    # Обновляем запись в базе данных с результатом qa
    db_file_data.test = qa_text_json
    db_file_data.qa_time = int(execution_time)
    db.commit()


@app.get("/file/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    nltk.download('punkt')

    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    db_file_data = db.query(models.FileData).filter(models.FileData.file_id == file_id).first()
    if db_file_data is None:
        raise HTTPException(status_code=404, detail="File data not found")
    test = db.query(models.FileData.test).filter(models.FileData.file_id == file_id).first()
    json_test = json.loads(test[0]) if (test and test[0]) else ""
    title = nltk.sent_tokenize(db_file_data.content)
    proc_time = (db_file_data.summary_time or 0) + (db_file_data.qa_time or 0)

    response = {
        "file_id": db_file.id,
        "file_name": db_file.filename,
        "file_size": db_file.file_size if db_file.file_size else 0,
        "text_length": len(db_file_data.content) if db_file_data.content else 0,
        "summary_length": len(db_file_data.summary) if db_file_data.summary else 0,
        "questions_count": len(json_test) if json_test else 0,
        "proc_time": proc_time if db_file_data.summary_time or db_file_data.qa_time else 0,
        "created_at": db_file.upload_date,
        "title": title[0] if title else "",
        "text": db_file_data.content if db_file_data.content else "",
        "summary": db_file_data.summary if  db_file_data.summary else "",
        "test": json_test
    }

    return response


@app.delete("/file/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()
    return {"message": "File and associated data deleted"}
