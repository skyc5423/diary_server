from fastAPIMessage import FastAPIMessage
from diaryHelper import DiaryHelper
from database.databaseHelper import SessionLocal
from database.db_classes import Diary, User
from base import UserCreate, DiaryCreate, DiaryResponse
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()
diary_helper = DiaryHelper()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/diaries/", response_model=DiaryCreate)
def create_diary(diary: DiaryCreate, db: Session = Depends(get_db)):
    db_diary = Diary(**diary.dict())
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary


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


@app.post("/generate")
async def generate_tasks(message: FastAPIMessage):
    return diary_helper(message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
