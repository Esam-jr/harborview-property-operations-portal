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

## Project Structure
- `frontend/` Vue app skeleton with router, pages, and reusable components
- `backend/` FastAPI app skeleton with modular `routers/`, `models/`, `services/`, `schemas/`, and `db/`
- `docker-compose.yml` local orchestration for frontend, backend, and PostgreSQL

Business logic is intentionally not implemented yet.
