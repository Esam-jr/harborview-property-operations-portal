# HarborView Property Operations Portal

Production-ready scaffold for a full-stack, offline-capable property operations platform.

## Stack
- Frontend: Vue 3 + Vite
- Backend: FastAPI (Python 3.10)
- Database: PostgreSQL
- Orchestration: Docker Compose

## Run with Docker
```bash
docker compose up --build
```

Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`  
API Health: `http://localhost:8000/api/v1/health/`

## Optional Offline Install Mode (Frontend)
Set `VITE_ENABLE_OFFLINE_MODE=true` when building/running the frontend to enable:
- Installable app experience (desktop/tablet/kiosk)
- Offline shell support via service worker
- Cached fallback for previously loaded GET API responses

Example:
```bash
cd frontend
VITE_ENABLE_OFFLINE_MODE=true npm run build
```

PowerShell example:
```powershell
cd frontend
$env:VITE_ENABLE_OFFLINE_MODE = "true"
npm run build
```

## Project Structure
- `frontend/` Vue app skeleton with router, pages, and reusable components
- `backend/` FastAPI app skeleton with modular `routers/`, `models/`, `services/`, `schemas/`, and `db/`
- `docker-compose.yml` local orchestration for frontend, backend, and PostgreSQL

Business logic is intentionally not implemented yet.

## Test Runner
Run all backend unit and API tests with one command:

```bash
bash run_tests.sh
```

Test suites:
- `unit_tests/` for service logic
- `API_tests/` for auth, listings, and orders API flows
