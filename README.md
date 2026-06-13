# ZK Session Auth

A zero-knowledge session authentication architecture featuring a Next.js frontend and a FastAPI backend. This project demonstrates a highly secure, JWT-less authentication flow using cryptographic challenge-response proofs and secure HttpOnly sessions, engineered for seamless deployment as a Vercel monorepo.

![Registration and Authentication Demo](assets/demo.webp)

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Deployment Guide](#deployment-guide)
- [Local Development](#local-development)
- [Usage Flow](#usage-flow)

## Architecture Overview

The application relies on a decoupled architecture where cryptographic operations are offloaded to the client, preventing private keys from ever being transmitted across the network. 

1. **Registration**: The user registers an identity by binding a username to a cryptographic public key.
2. **Challenge Request**: During login, the server issues a unique cryptographic challenge.
3. **Proof Verification**: The client computes a zero-knowledge proof, which the server verifies against the registered public key.
4. **Session Establishment**: Upon successful verification, the server issues a secure, short-lived HttpOnly session cookie.

## Key Features

- **Zero-Knowledge Authentication**: Secure login flow without transmitting or storing passwords or JWTs.
- **Challenge-Response Mechanism**: Prevents replay attacks by issuing unique, time-bound challenges.
- **Secure HttpOnly Sessions**: Mitigates Cross-Site Scripting (XSS) risks associated with local token storage.
- **Monorepo Design**: Integrated Next.js and FastAPI stack optimized for Vercel Serverless deployments with custom rewrites.

## Project Structure

```text
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
├── vercel.json            # Monorepo deploy config and edge rewrites
└── requirements.txt       # Local dev Python dependencies (with uvicorn)
```

## Deployment Guide

### Vercel Deployment

This project is configured for one-click deployment to Vercel via the `vercel.json` and Next.js configuration rewrites.

1. Push this repository to GitHub, GitLab, or Bitbucket.
2. Go to Vercel and import the repository.
3. Leave the **Root Directory** as `/` (the repository root). The `vercel.json` handles the build pipeline for both Next.js and FastAPI.
4. Configure the following environment variables in your Vercel project settings:

| Variable | Default | Description |
|---|---|---|
| `AUTH_MODE` | `dev_bypass` | Set to `zk` in production to enable real ZK proof verification. |
| `COOKIE_SECURE` | `false` | Set to `true` in production to enforce HTTPS-only cookies. |
| `COOKIE_SAMESITE` | `lax` | Cookie SameSite policy configuration. |
| `SESSION_TTL_SECONDS` | `900` | Session timeout duration (15 minutes). |
| `CHALLENGE_TTL_SECONDS` | `60` | Challenge expiration duration. |
| `REDIS_URL` | *In-memory store* | Required for persistent sessions across serverless cold starts. Add an Upstash Redis URL for production. |

5. Click **Deploy**.

## Local Development

### Backend (FastAPI)

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server (watches the app directory to prevent wiping in-memory sessions)
uvicorn app.main:app --reload --reload-dir app
```

### Frontend (Next.js)

```bash
cd frontend

# Set the backend URL for local proxying
cp .env.example .env.local  
# Ensure NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000 is set

# Install dependencies and start the development server
npm install
npm run dev
```

## Usage Flow

If you have just deployed the project or are running it locally, follow this flow to test the application:

### 1. Register an Identity
1. Navigate to the `/login` route.
2. Switch to the **register** tab.
3. Enter a desired username.
4. Enter a public key (or a dummy string if running in `dev_bypass` mode).
5. Submit the form. The cryptographic pipeline terminal will display the registration progression.

### 2. Authenticate
1. After registration, switch to the **login** tab.
2. Enter the registered username.
3. Run the authentication sequence. The client will automatically request a challenge, generate a mathematical proof, and send it for verification.
4. Upon successful verification, you will be redirected to the secure `/dashboard`.
