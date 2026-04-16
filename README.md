<div align="center">

<br />

```
███████╗██╗  ██╗    ███████╗███████╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
╚══███╔╝██║ ██╔╝    ██╔════╝██╔════╝██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
  ███╔╝ █████╔╝     ███████╗█████╗  ███████╗███████╗██║██║   ██║██╔██╗ ██║
 ███╔╝  ██╔═██╗     ╚════██║██╔══╝  ╚════██║╚════██║██║██║   ██║██║╚██╗██║
███████╗██║  ██╗    ███████║███████╗███████║███████║██║╚██████╔╝██║ ╚████║
╚══════╝╚═╝  ╚═╝    ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                    AUTH
```

**JWT-less authentication via challenge-response proofs and secure HttpOnly sessions**

<br />

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.2-000000?style=flat-square&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-session+challenge-DC382D?style=flat-square&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

</div>

---

## Overview

ZK Session Auth is a full-stack authentication system that eliminates JSON Web Tokens entirely. Instead of issuing a signed token that travels with every request, the server issues a **cryptographic challenge**, the client produces a **proof** (Schnorr / ECC-ready), and the server issues a short-lived **HttpOnly session cookie** on successful verification.

No passwords are stored. No tokens are transmitted in headers. No client-side secret ever leaves the browser in plaintext.

---

## Architecture

```
Browser
  │
  │  1. POST /auth/login/challenge  →  { challenge_id, challenge, expires_in }
  │  2. client signs challenge with private key  (Schnorr — dev_bypass in dev mode)
  │  3. POST /auth/login/verify     →  { R, s, challenge_id }
  │  4. server verifies proof, issues Set-Cookie: sid=<opaque>; HttpOnly
  │  5. GET /auth/me                →  { username }  (cookie auto-sent)
  │
  ▼
Next.js (frontend)  ─── /api/backend/* rewrite ───►  FastAPI (backend)
                                                            │
                                                            ▼
                                                         Redis
                                               challenge:{id}  →  TTL 60s
                                               session:{sid}   →  TTL 900s
```

The proof verification path is fully isolated in `app/crypto/verify.py` and accepts either **hex** or **base64url** encoded component strings, making it drop-in ready for any elliptic-curve library.

---

## Feature Highlights

| Feature | Detail |
|---|---|
| Zero passwords | Public-key identity — only a public key is registered |
| Challenge replay protection | Each challenge is one-time-use and expires in 60 seconds |
| Secure session cookie | `HttpOnly`, `SameSite=Lax`, optional `Secure` flag |
| Dev bypass mode | `AUTH_MODE=dev_bypass` skips proof verification for rapid local development |
| Proof format agnostic | Accepts hex or base64url — ready for secp256k1 / ed25519 |
| Animated UI | Framer Motion page transitions, live cryptographic pipeline log |
| TypeScript throughout | Fully typed frontend with strict `tsconfig` |

---

## Project Structure

```
auth-project/
├── app/                          # FastAPI backend
│   ├── config.py                 # Environment-driven settings
│   ├── db.py                     # Redis client (DummyRedis for local dev)
│   ├── main.py                   # Application entrypoint
│   ├── schemas.py                # Pydantic v2 request/response models
│   ├── crypto/
│   │   └── verify.py             # Proof parser + verification stub
│   ├── routes/
│   │   └── auth.py               # /auth/* endpoints
│   └── services/
│       ├── auth_service.py       # Login verification orchestration
│       ├── challenge_service.py  # Issue, fetch, mark-used challenge
│       └── session_service.py    # Create, get, destroy session
│
├── frontend/                     # Next.js 16 App Router frontend
│   ├── app/
│   │   ├── layout.tsx            # Root layout (Google Fonts, CSS vars)
│   │   ├── globals.css           # Design tokens, grain overlay, focus styles
│   │   ├── login/page.tsx
│   │   └── dashboard/page.tsx
│   ├── components/
│   │   ├── auth/AuthForm.tsx     # Login + register form with terminal log
│   │   ├── dashboard/DashboardClient.tsx
│   │   ├── layout/AppShell.tsx
│   │   ├── logs/TerminalLog.tsx  # Animated cryptographic pipeline stream
│   │   ├── motion/PageTransition.tsx
│   │   └── ui/                  # Button, Card, Input, Skeleton
│   ├── lib/
│   │   ├── axios.ts              # Axios instance + error normalizer
│   │   ├── utils.ts              # cn(), formatTimestamp()
│   │   └── types/auth.ts        # Shared TypeScript interfaces
│   └── services/
│       └── authService.ts        # API call wrappers
│
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis (or use the built-in `DummyRedis` for local development — no Redis installation required)

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) configure environment
cp .env.example .env
# AUTH_MODE=dev_bypass (default) — skips proof verification
# AUTH_MODE=zk           — enables full proof checking

# Start the API server
uvicorn app.main:app --reload
# Running at http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure backend URL (optional — defaults to http://127.0.0.1:8000)
cp .env.example .env.local
# NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000

# Start the dev server
npm run dev
# Running at http://localhost:3000
```

---

## API Reference

All endpoints are prefixed with `/auth`.

### Register a public key identity

```
POST /auth/register
Content-Type: application/json

{
  "username": "neo_cipher",
  "public_key": "<hex or base64url encoded public key>"
}
```

```
200 OK
{ "message": "User registered" }
```

---

### Request a login challenge

```
POST /auth/login/challenge
Content-Type: application/json

{ "username": "neo_cipher" }
```

```
200 OK
{
  "challenge_id": "<urlsafe token>",
  "challenge":    "<32-byte hex nonce>",
  "expires_in":   60
}
```

---

### Submit proof and open a session

```
POST /auth/login/verify
Content-Type: application/json

{
  "username":     "neo_cipher",
  "challenge_id": "<from previous step>",
  "R":            "<Schnorr commitment — hex or base64url>",
  "s":            "<Schnorr scalar — hex or base64url>"
}
```

```
200 OK
{ "message": "Login success" }
Set-Cookie: sid=<opaque>; Path=/; HttpOnly; SameSite=Lax
```

---

### Get the current session user

```
GET /auth/me
Cookie: sid=<opaque>
```

```
200 OK
{ "username": "neo_cipher" }

401 Unauthorized  — if cookie is missing or session has expired
```

---

### Logout

```
POST /auth/logout
Cookie: sid=<opaque>
```

```
200 OK
{ "message": "Logged out" }
Set-Cookie: sid=; Max-Age=0   (cookie cleared)
```

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `AUTH_MODE` | `dev_bypass` | `dev_bypass` skips proof check; `zk` enforces it |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SESSION_TTL_SECONDS` | `900` | Session lifetime (15 minutes) |
| `CHALLENGE_TTL_SECONDS` | `60` | Challenge expiry window |
| `COOKIE_NAME` | `sid` | Name of the session cookie |
| `COOKIE_SECURE` | `false` | Set to `true` in production behind HTTPS |
| `COOKIE_SAMESITE` | `lax` | `lax` or `strict` |

---

## Replacing the Proof Stub

In production, replace the body of `verify_proof` in `app/crypto/verify.py` with a real Schnorr verifier:

```python
# app/crypto/verify.py

def verify_proof(public_key: str, challenge: str, R: str, s: str) -> bool:
    pk_bytes    = _safe_decode_proof_component(public_key)
    R_bytes     = _safe_decode_proof_component(R)
    s_scalar    = int.from_bytes(_safe_decode_proof_component(s), "big")
    msg_bytes   = bytes.fromhex(challenge)

    # Drop in: py_ecc, cryptography, tinyec, fastecdsa, ...
    return schnorr_verify(pk_bytes, msg_bytes, R_bytes, s_scalar)
```

The input parsing, error handling, and challenge-lifecycle guard-rails are already in place — only the cryptographic primitive needs to change.

---

## Security Notes

- Challenges are **single-use**: `mark_challenge_used` atomically flags the key in Redis before a session is created, preventing replay.
- Sessions are **opaque tokens** stored server-side — there is no decodable payload on the client.
- `AUTH_MODE=dev_bypass` must never reach production. The config emits a `WARNING` log every time it is exercised.
- Public keys are stored in-memory (`USERS` dict in `routes/auth.py`) — replace with a persistent store before any production deployment.

---

## Development Workflow

```
# Terminal 1 — backend with auto-reload
uvicorn app.main:app --reload

# Terminal 2 — frontend with Turbopack
cd frontend && npm run dev
```

The frontend proxies all `/api/backend/*` requests to the FastAPI server via Next.js rewrites, so no CORS configuration is required during local development.

---

## License

MIT — see [LICENSE](LICENSE) for details.
