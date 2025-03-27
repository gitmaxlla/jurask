import fastapi
from fastapi.staticfiles import StaticFiles

from .llm import answer
from .data_models import UserQuestion, GeneratedResponse


app = fastapi.FastAPI()

@app.post("/")
async def generate_answer(input: UserQuestion) -> str:
    result = answer(input.contents)
    return result.answer # TODO: return GeneratedResponse

# Mount a static webpage to the root GET request
app.mount("/", StaticFiles(directory="project/static/", html=True), name="root")