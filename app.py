from diaryHelper import DiaryHelper
from database.databaseHelper import get_db, get_test_db
from database.db_classes import Diary, User
from base import UserCreate, UserResponse, DiaryCreate, DiaryResponse, RAGQuery, RAGResponse
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()
diary_helper = DiaryHelper()


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{email}/", response_model=UserResponse)
def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# remove user by id
@app.delete("/users/{user_id}/")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Diary not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}


@app.post("/diaries/", response_model=DiaryResponse)
def create_diary(diary: DiaryCreate, db: Session = Depends(get_db)):
    db_diary = db.query(Diary).filter(Diary.userId == diary.userId,
                                      Diary.date == diary.date).first()
    if db_diary is None:
        generated_content, is_valid = diary_helper.generate_content(diary.rawInput)
        diary.content = generated_content
        diary.rawInput = [diary.rawInput]
        db_diary = Diary(**diary.dict())
        if is_valid:
            db.add(db_diary)
            db.commit()
            db.refresh(db_diary)
        response_diary = DiaryResponse(**db_diary.__dict__)
        response_diary.isValid = is_valid
        return response_diary
    else:
        diary.rawInput = db_diary.rawInput + [diary.rawInput]
        generated_content, is_valid = diary_helper.generate_content(diary.rawInput)
        diary.content = generated_content
        db_diary.content = generated_content
        db_diary.rawInput = diary.rawInput
        if is_valid:
            db.commit()
            db.refresh(db_diary)
        response_diary = DiaryResponse(**db_diary.__dict__)
        response_diary.isValid = is_valid
        return response_diary



@app.get("/users/{user_id}/diaries/", response_model=List[DiaryResponse])
def get_diaries_for_user(user_id: int, db: Session = Depends(get_db)):
    diaries = db.query(Diary).filter(Diary.userId == user_id).all()
    return diaries


@app.get("/diaries/{diary_id}/", response_model=DiaryResponse)
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if diary is None:
        raise HTTPException(status_code=404, detail="Diary not found")
    return diary


@app.put("/diaries/{diary_id}/", response_model=DiaryResponse)
def update_diary(diary_id: int, diary: DiaryCreate, db: Session = Depends(get_db)):
    db_diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if db_diary is None:
        raise HTTPException(status_code=404, detail="Diary not found")

    if db_diary.content != diary.content:
        setattr(db_diary, 'content', diary.content)
    elif db_diary.rawInput != diary.rawInput:
        setattr(db_diary, 'rawInput', diary.rawInput)

    for key, value in diary.dict().items():
        setattr(db_diary, key, value)
    db.commit()
    db.refresh(db_diary)
    return db_diary


@app.delete("/diaries/{diary_id}/")
def delete_diary(diary_id: int, db: Session = Depends(get_db)):
    db_diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if db_diary is None:
        raise HTTPException(status_code=404, detail="Diary not found")
    db.delete(db_diary)
    db.commit()
    return {"detail": "Diary deleted successfully"}


@app.post("/test/")
def create_diary(diary: DiaryCreate, db: Session = Depends(get_db)):
    # generated_content, is_valid = diary_helper.generate_content(diary.rawInput)
    generated_content = 'Test Contents'
    is_valid = True
    diary.content = generated_content
    db_diary = Diary(**diary.dict())
    # if is_valid:
    #     db.add(db_diary)
    #     db.commit()
    #     db.refresh(db_diary)
    response_diary = DiaryResponse(**db_diary.__dict__)
    response_diary.isValid = is_valid
    return response_diary


@app.post("/rag/", response_model=RAGResponse)
def execute_rag(rag_query: RAGQuery, db: Session = Depends(get_db)):
    answer = diary_helper.execute_rag(rag_query.query)
    response_rag = RAGResponse(**rag_query.__dict__)
    response_rag.answer = answer
    return response_rag


# Ping API
@app.get("/ping")
def ping():
    return {"ping": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
