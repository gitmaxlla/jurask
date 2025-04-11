<img src="project/static/jurask_logo.png" alt="jurask logo" width=50>

# Jurask Project

> Your intelligent juridical document look-up tool.

---

## Features
* Supported law base:
  * Контитуция РФ
  * TODO:
  * ФЗ "О защите прав потребителей"
  * ФЗ "Об ООО"
  * ФЗ "Об АО"
  * ФЗ "Об образовании"
  * ФЗ "О рекламе"
*  API requirements
   *  Groq API key
*  Query language
   *  Russian

## Intial Setup
All commands should be run while in the ``jurask/`` folder

### 0. Install project dependencies
> pip install -r requirements.txt

### 1. Parse and save data from web
> python -m project.parse

### 2. Build vector database
> python -m project.vector_db

## Run the app
> uvicorn project.web:app

Then, open ``http://localhost:8000`` in your browser.

---

Alternatively, you may also make queries through the CLI. Just run
> python -m project.llm

and wait until you're prompted to enter your question with a dinosaur-styled invitation: ``jurask ---^*>``

## Technology
Built with **Langchain**, **Milvus**, and **FastAPI**.

## Known problems
1. No token limit considerations both for LLM and vector embeddings
2. ReAct should be implemented to allow answering questions requiring more than one retrieval

## Logo mascot lore?

Troodon Juryik does not come from the Jurassic era, but surprisingly you can still jurask him if you want.

deployment: local, zilliz
700 words limit to ensure input token limit does not run out (continuous)
(or 4500 - per minute)

(статья утратила силу)
(год обновления датасета)