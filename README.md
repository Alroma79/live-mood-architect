# Live Mood Architect

Full-stack app with a FastAPI backend and a Vite + React frontend.

## Backend (FastAPI)

From `backend/`:

1. `python -m venv .venv`
2. `./.venv/Scripts/Activate.ps1`
3. `pip install -r requirements.txt`
4. `uvicorn main:app --reload`

Health check: `GET /health` returns `{"status": "ok"}`.

## Frontend (Vite + React + TypeScript)

From `frontend/`:

1. `npm install`
2. Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` if needed.
3. `npm run dev`

Default frontend dev URL: `http://localhost:5173`.
Default backend API URL used by frontend: `http://127.0.0.1:8000`.

If the frontend shows "cannot reach server", ensure the backend is running on http://127.0.0.1:8000 and that CORS allows http://localhost:5173.
