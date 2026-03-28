# HarborView Property Operations Portal

HarborView is a full-stack property operations portal with a Vue frontend and FastAPI backend.

## Tech Stack
- Frontend: Vue 3 + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- Orchestration: Docker Compose

## Run The Platform
From this `repo/` directory:

```bash
docker compose up --build
```

## Service URLs
- Frontend: `http://localhost:5173`
- Backend root: `http://localhost:8000/`
- API base: `http://localhost:8000/api/v1`
- Health check: `http://localhost:8000/api/v1/health/`
- PostgreSQL: `localhost:5432` (`harborview` / `harborview`)

## Optional Offline Mode (Frontend)
Set `VITE_ENABLE_OFFLINE_MODE=true` to enable installable PWA behavior.

PowerShell:

```powershell
cd frontend
$env:VITE_ENABLE_OFFLINE_MODE = "true"
npm run build
```

Bash:

```bash
cd frontend
VITE_ENABLE_OFFLINE_MODE=true npm run build
```

## Test Instructions
From the workspace root (`harborview-property-operations-portal/`):

```bash
bash run_tests.sh
```

Direct pytest alternative:

```bash
python -m pytest unit_tests/ API_tests/ -v
```

Extra module-scoped tests under `repo/backend/`:

```bash
python -m pytest repo/backend/unit_tests repo/backend/API_tests -v
```

## Backend Dependency Setup
From `repo/backend`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Password hashing compatibility stack:
- `passlib[argon2,bcrypt]==1.7.4`
- `argon2-cffi==23.1.0`
- `bcrypt==3.2.0`
