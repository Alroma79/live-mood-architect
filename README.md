# Live Mood Architect

Full-stack app with a FastAPI backend and a Vite + React frontend.

## Environment Variables

### Backend (`backend/.env`)

- `OPENAI_API_KEY` (required): OpenAI API key.
- `FRONTEND_ORIGIN` (required in deployed environments): allowed CORS origin(s). Use comma-separated values when needed.
  - Example: `http://localhost:5173,https://your-vercel-app.vercel.app`
- `OPENAI_MODEL` (optional): defaults to `gpt-4o-mini`.

### Frontend (`frontend/.env`)

- `VITE_API_BASE_URL` (required): backend base URL.
  - Local default: `http://127.0.0.1:8000`
  - Production example: `https://live-mood-architect-production.up.railway.app`

## Local Setup

### Backend Setup (one-time)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Frontend Setup (one-time)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
```

## Run Locally

### Backend (single command after setup)

```powershell
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload
```

### Frontend (single command after setup)

```powershell
cd frontend; npm run dev
```

## API Verification

### `curl` example

```bash
curl -X POST "http://127.0.0.1:8000/api/affirmation" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alex\",\"feeling\":\"a little overwhelmed but hopeful\"}"
```

### PowerShell example

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/affirmation" `
  -ContentType "application/json" `
  -Body '{"name":"Alex","feeling":"a little overwhelmed but hopeful"}'
```

Health check: `GET /health` returns `{"status":"ok"}`.

## Deployment Notes

### Railway (backend)

- Service root directory: `/backend`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Required env vars:
  - `OPENAI_API_KEY`
  - `FRONTEND_ORIGIN` (must include your Vercel URL)
- Optional env var:
  - `OPENAI_MODEL`

### Vercel (frontend)

- Required env var:
  - `VITE_API_BASE_URL` (set to your Railway backend URL)

If the frontend shows "cannot reach server", ensure the backend is running/reachable and that `FRONTEND_ORIGIN` includes your Vercel domain and local dev origin.
