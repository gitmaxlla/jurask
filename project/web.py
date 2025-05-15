import fastapi
import fastapi.middleware
import fastapi.middleware.cors
from fastapi.staticfiles import StaticFiles
import uvicorn

from .llm import answer, load_index
from .reference_db import search_database
from .data_models import ReferenceSearch, UserQuestion


DATABASE_PATH = None
app = fastapi.FastAPI()

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/")
async def generate_answer(input: UserQuestion): # TODO: Pydantic
    return answer(input.contents, load_index())

@app.post("/ref")
async def get_original(query: ReferenceSearch): # TODO: Pydantic
    return {"content": search_database(DATABASE_PATH, query.document, query.name)}

# Mount a static webpage to the root GET request
app.mount("/", StaticFiles(directory="project/static/", html=True), name="root")

def main(datasets, paths):
    global DATABASE_PATH
    DATABASE_PATH = paths["database-path"]
    uvicorn.run("project.web:app", reload=False)