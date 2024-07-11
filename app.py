from fastapi import FastAPI
from fastAPIMessage import FastAPIMessage
from diaryHelper import DiaryHelper

app = FastAPI()
diary_helper = DiaryHelper()


@app.post("/generate")
async def generate_tasks(message: FastAPIMessage):
    return diary_helper(message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
