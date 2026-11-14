# AI Resume Builder development roadmap

## Where you left off

- `076f6be` scaffolded the React and Vite frontend.
- `f107365` added PostgreSQL and Qdrant to Docker Compose.
- `cf3013c` added the FastAPI application.
- `bf454ae` connected the frontend to the API health endpoint.

The frontend can ask the API for its health status. The API does not yet save resumes or check a database connection. Your next milestone is saving one resume from the browser and reopening it by ID.

## 1. Prepare the local environment

- [ ] Review and commit the current repository cleanup on its own.
- [ ] Keep your working copy of `infrastructure/.env`, add that path to `.gitignore`, and untrack it with `git rm --cached -- infrastructure/.env`. Add `infrastructure/.env.example` with placeholder values and document how to copy it for local setup. Rotate the PostgreSQL password if the committed value is used outside local development.
- [ ] Start PostgreSQL from the repository root with `docker compose -f infrastructure/docker-compose.yml up -d postgres`. Check its status with `docker compose -f infrastructure/docker-compose.yml ps postgres`.
- [ ] Start FastAPI with `python -m uvicorn backend.app.main:app --reload` using your activated Python environment. In a second terminal, run `npm run dev` from `frontend`. Open `http://localhost:5173` and confirm the page displays a healthy backend.

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
