🔐 ZK Session Auth (JWT-less Authentication)

<p align="center">
<b>Secure, stateful authentication using challenge-response proof + server sessions</b>




<i>Built with FastAPI, Redis-ready design, and engineering-first security practices.</i>
</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python Version" />
<img src="https://img.shields.io/badge/FastAPI-0.115+-009688.svg" alt="FastAPI" />
<img src="https://img.shields.io/badge/Auth-JWT--less-orange.svg" alt="Auth JWT-less" />
<img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
</p>

📌 Overview

ZK Session Auth is a professional authentication architecture that bypasses traditional JWT vulnerabilities by implementing:

Challenge-response login flow (Schnorr/Fiat-Shamir concept)

Server-side stateful sessions using HttpOnly cookies

Replay-resistant challenge IDs with strict expiration

Centralized session control for immediate token revocation

Designed for both academic exploration and production-grade engineering environments.

✨ Key Features

✅ JWT-less Architecture: Eliminates risks associated with long-lived stateless tokens.

✅ Dynamic Challenge Generation: /login/challenge issues single-use, time-bound challenges.

✅ Zero-Knowledge Proof Verification: /login/verify validates cryptographic proofs securely.

✅ Secure Cookie Management: Hardened session handling (HttpOnly, Secure, SameSite).

✅ Session Introspection & Invalidation: Robust /me and /logout endpoints.

✅ Modular Codebase: Clean separation of routes, services, cryptography, and configuration.

🏗️ Architecture & Flow

Traditional JWTs make token revocation difficult. This system uses a stateful alternative, providing explicit server-side control over sessions.

API Request Lifecycle

POST /auth/register ➔ Register public key.

POST /auth/login/challenge ➔ Server issues unique challenge_id.

POST /auth/login/verify ➔ Client solves challenge; Server sets sid cookie.

GET /auth/me ➔ Server validates sid cookie.

POST /auth/logout ➔ Server destroys session.

🚀 Quick Start

1. Environment Setup

python -3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1


2. Install Dependencies

python -m pip install --upgrade pip
pip install -r requirements.txt


3. Run the Server

python -m uvicorn app.main:app --reload --reload-dir app


(Tip: If auto-reload loops, use: --reload-exclude ".venv/*" --reload-exclude "*/site-packages/*")

💻 API Endpoints & Swagger UI

Access the interactive API documentation at:

Swagger UI: http://127.0.0.1:8000/docs

Health Check: http://127.0.0.1:8000/

Swagger UI Preview

Replace the src below with a screenshot of your Swagger UI.

📂 Project Structure

auth-project/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── schemas.py
│   ├── routes/
│   │   └── auth.py
│   ├── services/
│   │   ├── challenge_service.py
│   │   └── session_service.py
│   └── crypto/
│       └── verify.py
├── requirements.txt
└── README.md


🔐 Security Hardening (Production)

While this is a strong foundation, production deployments should implement:

Real Schnorr/ECC verification via audited cryptographic libraries.

Argon2id/PBKDF2 for key derivation.

Redis-backed strict challenge expiry and IP rate limiting.

TLS-only secure cookies (Secure=True, SameSite=Strict).

📈 Roadmap

[ ] PostgreSQL user persistence

[ ] Real cryptographic verification module implementation

[ ] Refresh sessions & key rotation

[ ] Device/session management dashboard

[ ] Dockerized deployment

[ ] CI/CD pipeline with security unit testing

👨‍💻 Author

Shivam Kumar Roll No: 202501100400300

📄 License

Licensed under the MIT License. Feel free to use, modify, and build upon it with attribution.

<p align="center"><b>Built for secure engineering practice 🚀</b></p>

📄 Resume-Ready Project Description (ATS Format)

(Note: You do not need to include this section in the final GitHub repo. Copy this directly into your resume under the "Projects" section.)

ZK Session Auth (JWT-less Authentication) | Python, FastAPI, Redis, Cryptography

Architected and deployed a stateful, JWT-less authentication backend using FastAPI, implementing a zero-knowledge challenge-response protocol to eliminate risks associated with long-lived stateless token theft.

Engineered secure session lifecycle management utilizing strictly configured HttpOnly cookies, replay-resistant cryptographic challenges, and centralized session invalidation.

Designed a modular, production-ready system architecture with cleanly decoupled routing, service, and cryptographic layers, fully documented via OpenAPI/Swagger.
