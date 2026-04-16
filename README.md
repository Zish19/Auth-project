# zk-session-auth

A zero-knowledge session authentication project with a **Next.js** frontend and **FastAPI** backend, deployable as a monorepo to [Vercel](https://vercel.com).

## Project Structure

```
auth-project/
├── api/                   # Vercel Python Serverless Function
│   ├── index.py           # FastAPI entry point (Mangum-wrapped)
│   └── requirements.txt   # Python dependencies for the function
├── app/                   # FastAPI application package (shared)
│   ├── config.py
│   ├── db.py
│   ├── schemas.py
│   ├── routes/
│   ├── services/
│   └── crypto/
├── frontend/              # Next.js application
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── services/
│   └── ...
├── vercel.json            # Monorepo deploy config
└── requirements.txt       # Local dev Python deps (with uvicorn)
```

## Deploying to Vercel

### One-click deploy (recommended)

1. Push this repository to GitHub / GitLab / Bitbucket.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Leave the **Root Directory** as `/` (the repo root) — `vercel.json` handles everything.
4. Add the environment variable **`COOKIE_SECURE=true`** in Vercel project settings.
5. Click **Deploy**.

### Environment Variables

Set these in your Vercel project → Settings → Environment Variables:

| Variable | Default | Description |
|---|---|---|
| `AUTH_MODE` | `dev_bypass` | Set to `zk` in production to enable real ZK proof verification |
| `COOKIE_SECURE` | `false` | Set to `true` in production (HTTPS cookies) |
| `COOKIE_SAMESITE` | `lax` | Cookie SameSite policy |
| `SESSION_TTL_SECONDS` | `900` | Session timeout (15 min) |
| `CHALLENGE_TTL_SECONDS` | `60` | Challenge expiry |
| `REDIS_URL` | *(DummyRedis in-memory)* | Optional: add a Redis URL (e.g., Upstash) for persistent sessions |

> **Note:** Without a `REDIS_URL`, the backend uses an in-memory store. Sessions are lost on every cold start. For production, add an [Upstash Redis](https://upstash.com) URL.

## Local Development

### Backend (FastAPI)

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Next.js)

```bash
cd frontend
cp .env.example .env.local  # set NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
npm install
npm run dev
```

## How it works on Vercel

```
Browser
  └─► GET/POST /api/backend/*  ──► Vercel routes ──► api/index.py (Python Serverless)
  └─► GET /*                   ──► Vercel routes ──► frontend/ (Next.js)
```

The `vercel.json` at the repo root configures two build targets:
- `@vercel/next` builds the Next.js app from `frontend/`
- `@vercel/python` builds the FastAPI function from `api/index.py`
