import fastapi
import json
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .llm import *

class Question(BaseModel):
    contents: str


app = fastapi.FastAPI()

@app.post("/")
async def generate_answer(input: Question) -> str:
    result = answer(input.contents)
    return result.answer

app.mount("/", StaticFiles(directory="project/pages/", html=True), name="root")