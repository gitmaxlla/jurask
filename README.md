# Jurask Project
> Your intelligent juridical document look-up tool.
---

## Features
* Supported law base:
  * Russian Constitution
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
