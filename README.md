# Live Mood Architect

Full-stack app with a FastAPI backend (Railway) and a Vite + React frontend (Vercel).

## Environment Variables

### Backend (`backend/.env`)

- `OPENAI_API_KEY` (required)
- `FRONTEND_ORIGIN` (required in deployed environments, comma-separated if multiple)
  - Example: `http://localhost:5173,https://your-vercel-app.vercel.app`
- `OPENAI_MODEL` (optional, default: `gpt-4o-mini`)

### Frontend (`frontend/.env`)

- `VITE_API_BASE_URL` (required)
  - Local: `http://127.0.0.1:8000`
  - Production: `https://live-mood-architect-production.up.railway.app` (no trailing slash)

## Local Setup (One-Time)

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
```

## Run Locally

### Backend (single command)

```powershell
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload
```

### Frontend (single command)

```powershell
cd frontend; npm run dev
```

## Deploy

### Railway (Backend)

1. Create/use a Railway service for this repo.
2. Set service **Root Directory** to `backend`.
3. Set **Start Command** to:
   - `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set required env vars:
   - `OPENAI_API_KEY`
   - `FRONTEND_ORIGIN` (must include your Vercel app URL and any local origins you use)
5. Optional env var:
   - `OPENAI_MODEL`

The start command above explicitly binds `0.0.0.0` and listens on Railway-provided `$PORT`.

### Vercel (Frontend)

1. Import this repo in Vercel.
2. Set project **Root Directory** to `frontend`.
3. Set env var:
   - `VITE_API_BASE_URL=https://live-mood-architect-production.up.railway.app`
4. Ensure there is **no trailing slash** in `VITE_API_BASE_URL`.
5. Deploy.

## Verification

### `curl` (backend endpoint)

```bash
curl -X POST "http://127.0.0.1:8000/api/affirmation" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alex\",\"feeling\":\"a little overwhelmed but hopeful\"}"
```

### PowerShell (backend endpoint)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/affirmation" `
  -ContentType "application/json" `
  -Body '{"name":"Alex","feeling":"a little overwhelmed but hopeful"}'
```

### Browser DevTools (frontend to backend)

1. Open deployed frontend in browser.
2. Submit the form once.
3. Open DevTools -> Network.
4. Confirm `POST /api/affirmation` returns `200 OK`.
5. Confirm response contains JSON with `affirmation`.

Health check: `GET /health` returns `{"status":"ok"}`.

## Submission Notes

### Architecture (ASCII)

```text
[User Browser]
      |
      v
[Vercel Frontend: React/Vite]
      |
      | POST /api/affirmation
      v
[Railway Backend: FastAPI]
      |
      | chat.completions.create
      v
[OpenAI API]
```

### Security Notes

- Secrets are environment variables only (`OPENAI_API_KEY` is never committed).
- `.env` files are ignored by git; only `.env.example` files are tracked.
- Backend logs are metadata-only (`request_id`, durations, lengths, status) and do not log user text.

### Known Limitations

- Self-harm detection uses a simple keyword regex and can miss edge cases.
- No persistent storage yet (requests and outputs are not stored).
- No automated test suite is included yet for endpoint-level regression checks.
