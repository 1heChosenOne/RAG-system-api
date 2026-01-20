# RAG-system-api
https://github.com/user-attachments/assets/2f3d86e1-8f12-4e15-a439-3396c493a53d
Overview
--------
RAG system api is an API of Retrieval-Augmented Generation (RAG) system implemented in Python. The project demonstrates building and querying vector indexes for user-specific document stores, providing a structure for experimenting with local embeddings, FAISS indexes, and simple retrieval workflows integrated into a Python application.

My RAG system utilizes FastAPI, FAISS, PostgreSQL DB, Sqlalchemy, Authx, Pydantic, Hashing(bcrypt), Tokenizing(tiktoken) ,Uvicorn to host and Groq as cloud LLM model

This repository is intended for developers and researchers who want a lightweight RAG environment. It focuses on modularity, readability, and quick iteration.

Repository Structure
--------------------
- `schemas.py`: Pydantic models and request/response schemas used by API routes.
- `db.py`: Database helpers — connection provider, table creation and light SQL utilities (Postgres + SQLAlchemy).
- `utils.py`: Shared utilities — tokenization/encoding, embedding model instance, AuthX setup, filename validation, and `data/users/` path helpers.
- `main.py`: Application entrypoint — creates FastAPI app, registers routers and exception handlers, and runs example flows.
- `requirements.txt`: Python package dependencies for the project.
- `README.md`: Project overview, setup, and usage (this file).
- `LICENSE`: Project license.
- `infra/`: Infrastructure helpers:
  - `indexer.py` (FAISS index create/load/search)
  - `embeddings.py` (embedding wrappers)
  - `groq.py` (Groq LLM integration)
- `repos/`: Database repository layer (e.g., `files.py` managing file and chunk DB operations).
- `routes/`: FastAPI route modules (e.g., `files.py` exposing the public API endpoints).
- `services/`: Business logic services (e.g., `auth.py` for auth, `profile.py` for file workflows).
- `exceptions.py` and `exception_handlers.py`: Custom exceptions and FastAPI handlers to standardize error responses.

Key Features
------------
- Per-user FAISS vector indexes stored under `data/users/` for isolation and fast retrieval.
- Simple, modular code split across a few files for easy understanding and extension.
- Basic utilities for preprocessing, creating embeddings, and querying the index.

Endpoints
---------
- GET /my_files: Returns list of files for the authenticated user. Requires auth (cookie token). Query params: none. Response: list of file records or {"msg":"no loaded files on server"}.

- POST /sign_up: Register a new user. Body: `PassEmail` (email, password). Response: {"msg":"Succesful registation"} or error for duplicate email.

- POST /log_in: Log in and set access cookie. Body: `PassEmail` (email, password). Response: cookie set (cookie name: `my_access_token`) + success message or error.

- POST /addfile: Upload a `.txt` file (only `.txt` allowed). The file is chunked, embeddings are computed, a per-user FAISS index is written and file/chunk records are stored in the DB. Requires auth. Form file: `UploadFile`. Response: {"msg":"file added successfully with id <id> and name <name>"}.

- DELETE /delete_file: Delete a file by `file_id` (int) for the authenticated user. Requires auth. Response: success or not-found message; removes FAISS index file at `data/users/user_{owner_id}/index_faiss_{file_id}.faiss` if present.

- POST /chat: Run retrieval + LLM completion against a specific file. Requires auth. Body: `FileQuestion` (file_id, question). Returns LLM text (via Groq client) or error messages if file/index missing.

Getting Started (Windows)
-------------------------
These instructions assume you're on Windows (PowerShell) and have Python 3.10+ installed.

1. Clone the repository

   git clone https://github.com/1heChosenOne/RAG-system-api
   cd "`YOUR path to directory`"

2. Create and activate a virtual environment

   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. Install dependencies

   pip install -r requirements.txt

4. Run the example

   python main.py

5. Create .env file with your own environment variables

6. Run server using uvicorn main:app or other command with "main" as main file

Configuration & Environment
---------------------------
- `requirements.txt`: install the listed packages.
- Environment variables: add `JWT_SECRET_KEY`, `GROQ_API_KEY`, and `DB_URL` to a `.env` file. The Groq API key is used by the Groq client; the JWT secret is used by AuthX.
- Token expiration and cookie name are configurable in `utils.py` (`AuthXConfig`); by default the access cookie name is `my_access_token` and expiration is set in seconds.

Usage
-----
The repository includes a `main.py` file that demonstrates the typical flow:

1. Load or create a per-user FAISS index under `data/users/{user_id}>/index_faiss_{file_id}.faiss`.
2. Create or load embeddings for documents.
3. Run a similarity query against the index and retrieve top-k documents.
4. Perform downstream steps (e.g., prompt generation, LLM completion) using the retrieved context.

Typical commands (examples):

  python main.py --user user_1 --query "How do I reset my password?"

(Check `main.py` for exact CLI flags or replace with direct function calls for programmatic usage or use uvicorn to host on local address)

Code Walkthrough
----------------
- `schemas.py`  
  Core Pydantic data classes and lightweight models used throughout the application, including:
  - Documents  
  - Index metadata  
  - Query results  

- `db.py`  
  Database helper functions and utilities:
  - Connection provider  
  - Table creation helpers  
  - Simple SQL utilities  
  Supports PostgreSQL via SQLAlchemy.  

- `utils.py`  
  Shared utility functions across the project, including:
  - Text tokenization and encoding  
  - Embedding model instance management  
  - Authentication configuration (AuthX)  
  - Filename validation  
  - Helpers for managing `data/users/` paths  

- `main.py`:
  - Entry point of the FastAPI application.
  - Initializes the FastAPI app instance.
  - Includes `files` router to expose all API endpoints.
  - Registers global exception handlers via `register_handlers(app)`.
  - Performs startup tasks such as creating necessary database tables.

- `infra/`  
  - `indexer.py`: Functions to create, load, and search FAISS indexes  
  - `embeddings.py`: Wrapper around embedding model (`sentence-transformers`) with helper functions like `np_embed_texts` and `embed_text`  
  - `groq.py`: Groq client integration and `chat_response` function to prepare prompts and call the LLM  

- `repos/`  
  - `files.py`: Database access layer for files and chunks, supporting insert, select, and delete operations used by services  

- `routes/`  
  - `files.py`: FastAPI routes exposing main API endpoints:
    - `/sign_up`  
    - `/log_in`  
    - `/addfile`  
    - `/delete_file`  
    - `/my_files`  
    - `/chat`  

- `services/`  
  - `auth.py`: Handles user registration and login, including:
    - Password hashing  
    - Token/cookie management  
  - `profile.py`: High-level business logic for file upload (chunking, storing chunks, building indexes), retrieval (`chat` flow), listing, and deletion  

- `exceptions.py` and `exception_handlers.py`  
  Custom exception types and FastAPI exception handlers to standardize error responses across the API  

Data and Indexes
----------------
The `data/users/` directory contains per-user FAISS index files. Index files follow the pattern:

`data/users/user_{owner_id}/index_faiss_{file_id}.faiss`

Notes:
- Only `.txt` uploads are accepted and the service chunks text before embedding (defaults: chunk_size=300 tokens, overlap=70 tokens).
- Embeddings use `sentence-transformers` model `all-MiniLM-L6-v2` and tokenizer `text-embedding-3-small` is used for tokenization in the chunking pipeline.
- The project uses Groq for LLM completions (model configured in `infra/groq.py`, e.g. `llama-3.3-70b-versatile`).

Security & Privacy
------------------
- This project may process user documents; be mindful of storing sensitive information in plain text index files.
- If using remote embedding providers, guard API keys and consider privacy implications of sending content to external services.

Contributing
------------
Contributions are welcome. Suggested workflow:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Add or update code, and include tests where applicable.
4. Open a pull request with a clear description of changes.

License
-------
See the `LICENSE` file included in this repository for license terms.

Acknowledgements
----------------
This project was created as a compact local RAG workflow. Credit to the open-source FAISS project for the vector index implementation that makes local similarity search fast and easy to experiment with.

Contact
-------
If you have questions, feature requests, or bug reports, please open an issue in the repository.

