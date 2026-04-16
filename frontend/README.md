# ZK Session Auth Frontend

Production-ready Next.js frontend for a JWT-less auth workflow powered by:
- cryptographic challenge-response login (`/auth/login/challenge` + `/auth/login/verify`)
- server-side session cookies (HttpOnly)
- protected dashboard session UX

## Stack
- Next.js (App Router) + TypeScript (strict)
- Tailwind CSS
- Framer Motion
- Axios (with `withCredentials: true`)

## Local setup
1. Create env file:
   ```bash
   cp .env.example .env.local
   ```
2. Set backend URL in `.env.local`:
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
   ```
3. Install and run:
   ```bash
   npm install
   npm run dev
   ```

App runs at [http://localhost:3000](http://localhost:3000).

## Backend proxy behavior
Frontend requests go to `/api/backend/*` and are rewritten by `next.config.ts` to your FastAPI origin from `NEXT_PUBLIC_BACKEND_URL`.

This keeps cookie-auth ergonomics clean in local development and avoids direct cross-origin calls from components.

## Routes
- `/login` - register/login toggle with terminal-style challenge-response logs
- `/dashboard` - protected session dashboard (`/auth/me`) + logout

## Architecture
- `app/` - route pages and layout
- `components/auth/` - auth form and flow orchestration
- `components/logs/` - reusable terminal log stream UI
- `components/ui/` - shared primitives (`Button`, `Card`, `Input`, `Skeleton`)
- `components/motion/` - reusable page transition wrapper
- `lib/` - axios instance, types, and utilities
- `services/` - typed auth API service methods

## Production notes
- Includes loading skeletons and async state handling
- Includes ARIA live updates for terminal logs and focus-visible styles
- Uses modular service/type boundaries to keep scaling straightforward
