# Jurask Project
``Your intelligent juridical document look-up tool.``

* Supported law base:
  * Russian Constitution
*  API requirements
   *  Groq API key
*  Query language
   *  Russian

## Intial Setup

### 0. Install project dependencies
> pip install -r requirements.txt

### 1. Parse and save data from web
> python project/parser.py

### 2. Build vector database
> python project/vector_db.py
> 
## Run the app
> uvicorn project.web:app