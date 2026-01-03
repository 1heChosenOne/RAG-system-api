# RAG-system-api
Overview
--------
RAG system api is an API of Retrieval-Augmented Generation (RAG) system implemented in Python. The project demonstrates building and querying vector indexes for user-specific document stores, providing a structure for experimenting with local embeddings, FAISS indexes, and simple retrieval workflows integrated into a Python application.

My RAG system utilizes FastAPI, FAISS, PostgreSQL DB, Sqlalchemy, Authx, Pydantic, Hashing(bcrypt), Tokenizing(tiktoken) ,Uvicorn to host and Groq as cloud LLM model

This repository is intended for developers and researchers who want a lightweight RAG environment. It focuses on modularity, readability, and quick iteration.

Repository Structure
--------------------
- classes.py              - Core data classes and lightweight models used by the application.
- db.py                   - Database utility functions and simple persistence helpers.
- utils.py                - Helper utilities (text processing, embedding wrappers, IO helpers).
- main.py                 - Main application entrypoint / example runner.
- requirements.txt        - Python package dependencies.
- README.md               - This file (project overview, setup and usage).
- LICENSE                 - Project license.

Key Features
------------
- Per-user FAISS vector indexes stored under `data/users/` for isolation and fast retrieval.
- Simple, modular code split across a few files for easy understanding and extension.
- Basic utilities for preprocessing, creating embeddings, and querying the index.

Endpoints
---------
- GET /my_files: Returns list of files for the authenticated user. Requires auth (cookie token). Query params: none. Response: list of file records or {"msg":"no loaded files on server"}.

-   POST /sign_up: Register a new user. Body: pass_and_email (email, password). Response: {"msg":"Succesful registation"} or error for duplicate email.

- POST /log_in: Log in and set access cookie. Body: pass_and_email (email, password). Response: cookie set + success message or error.

- POST /addfile: Upload a .txt file, chunk it, compute embeddings, build per-user FAISS index and store file record. Requires auth. Form file: UploadFile. Response: {"msg":"file added succesfully with id <id> and anme <name>"}.

- DELETE /delete_file: Delete a file by file_id (int) for the authenticated user. Requires auth. Response: success or not-found message; removes FAISS index file if present.

- POST /chat: Run a retrieval + LLM completion against a specific file. Requires auth. Body: file_and_question (file_id, question). Returns LLM text (uses Groq client) or error messages if file/index missing.

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
- requirements.txt: install the listed packages.
- Environment variables: JWT_SECRET_KEY, GROQ_API_KEY ,DB_URL variables should be added in .env file 
- And by the way you can choose the token expiration time on utils.py

Usage
-----
The repository includes a `main.py` file that demonstrates the typical flow:

1. Load or create a per-user FAISS index under `data/users/{user_id}>/index_faiss_{file_id}.faiss`.
2. Create or load embeddings for documents.
3. Run a similarity query against the index and retrieve top-k documents.
4. Perform downstream steps (e.g., prompt generation, LLM completion) using the retrieved context.

Typical commands (examples):

  python main.py --user user_1 --query "How do I reset my password?"

(Check `main.py` for exact CLI flags or replace with direct function calls for programmatic usage or use uvicorn to host on local adress)

Code Walkthrough
----------------
- `classes.py`:
  - Contains data classes for documents, index metadata, and query results.

- `db.py`:
  - Functions for creating database ,creating tables in postgres and get connection function

- `utils.py`:
  - Preprocessing, text normalization, embedding wrappers (local/provider-agnostic), validation and helper functions for building FAISS indexes.

- `main.py`:
  - Script that ties together index loading, querying, and printing results. Use this as a starting point to build integrations or UI wrappers.

Data and Indexes
----------------
The `data/users/` directory contains per-user FAISS index files.

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

