# AI Resume Builder development roadmap

## Where you left off

- `076f6be` scaffolded the React and Vite frontend.
- `f107365` added PostgreSQL and Qdrant to Docker Compose.
- `cf3013c` added the FastAPI application.
- `bf454ae` connected the frontend to the API health endpoint.

The frontend can ask the API for its health status. The API does not yet save resumes or check a database connection. Your next milestone is saving one resume from the browser and reopening it by ID.

## 1. Prepare the local environment

Run commands from the repository root in PowerShell.

1. Install Python 3.13, Node.js 24 and Docker Desktop. If `.venv` is missing, create it with `py -3.13 -m venv .venv`. Install backend dependencies with `.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt` and check them with `.\.venv\Scripts\python.exe -m pip check`. Install frontend dependencies with `npm.cmd --prefix frontend ci`.
2. If `infrastructure/.env` is missing, run `Copy-Item infrastructure/.env.example infrastructure/.env` and set your local `POSTGRES_PASSWORD`. If the previously committed password is used elsewhere, rotate it there. Existing PostgreSQL volumes keep their original database password.
3. Start Docker Desktop. Run `docker compose -f infrastructure/docker-compose.yml up -d --wait`. PostgreSQL listens on localhost port 15432, and Qdrant uses 16333 for HTTP and 16334 for gRPC by default. Override the ports in `infrastructure/.env` if needed. Verify PostgreSQL with `docker compose -f infrastructure/docker-compose.yml exec -T postgres psql -U resume_user -d resume_db -c "SELECT 1;"` and Qdrant with `Invoke-RestMethod http://127.0.0.1:16333/readyz`.
4. Start FastAPI with `.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload`. From a second terminal run `npm.cmd --prefix frontend run dev`. Open the URL Vite prints and confirm **Backend status: healthy**. Vite forwards `/api/health` to port 8000. A deployed frontend needs equivalent `/api` routing.
5. Run `npm.cmd --prefix frontend run lint` and `npm.cmd --prefix frontend run build` before merging.

## 2. Save and retrieve one resume

- [ ] Read the PostgreSQL connection settings from the environment and configure a SQLAlchemy session for each API request.
- [ ] Create a resume table with an ID, a name, a summary, and structured experience entries. Add an Alembic migration and verify it applies to an empty database.
- [ ] Define Pydantic request and response models. Require a nonblank name and validate each experience entry.
- [ ] Implement `POST /resumes` to save a resume and return its ID with HTTP 201. Implement `GET /resumes/{id}` to return the saved data or HTTP 404 for an unknown ID.
- [ ] In Postman, create a resume, restart the API, and fetch the same ID. Also send an invalid payload and request an unknown ID to check validation and error responses.

## 3. Connect the React editor

- [ ] Replace the health-only screen with a form for the same fields as the API. Allow users to add and remove experience entries.
- [ ] Show errors next to invalid fields. While a save is in progress, disable the save button and show any request failure without clearing the form.
- [ ] After creating a resume, navigate to `/resumes/{id}`. Load the resume by ID when that URL opens directly.
- [ ] Create a resume in the browser, refresh its URL, and confirm the saved fields reload. Check what the page shows for an unknown ID and when the API is offline.

## 4. Add editing and a printable preview

- [ ] Add `PATCH /resumes/{id}`. Validate changes and preserve fields omitted from the request.
- [ ] Use the same form for editing. Add a preview that renders the saved data and a print layout the browser can export to PDF.
- [ ] Edit one experience entry, refresh the page, and confirm the change appears in both the editor and preview.

## 5. Add one AI feature

- [ ] Add a Generate summary button that uses the resume's experience entries to request a draft summary from the backend.
- [ ] Show the draft separately in the editor and let the user accept, edit, or discard it. If generation fails, keep the existing summary and allow a retry.
- [ ] Add Qdrant when a feature needs semantic retrieval, such as matching experience entries to a job description.

Before exposing the app to other users, add authentication and enforce resume ownership on every read and write.
