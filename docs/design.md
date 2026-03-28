# HarborView Design

## Architecture Overview
HarborView uses a layered backend architecture:
- `routers/`: HTTP endpoints, request parsing, role/object authorization checks.
- `services/`: Business logic and validation.
- `models/`: SQLAlchemy entities and enums.
- `schemas/`: Pydantic request/response contracts.
- `db/`: SQLAlchemy engine/session/base wiring.
- `api/deps/`: Shared dependencies (authentication, DB session).

The API is mounted under `/api/v1` in `app/main.py`.

## Runtime Topology
- Vue frontend runs on port `5173`.
- FastAPI backend runs on port `8000`.
- PostgreSQL runs on port `5432`.
- All services are orchestrated by `docker-compose.yml`.

## Authentication And Authorization
- Authentication is local username/password via `/api/v1/auth/login`.
- Access token is bearer JWT; identity subject is username.
- `get_current_user()` resolves token subject to a `User` object.
- Role enforcement happens in routers and services using `UserRole` enum:
  - `admin`
  - `manager`
  - `clerk`
  - `dispatcher`
  - `resident`

## Authorization Model
- Route-level authorization: checks role gates (for example manager-only listing management).
- Object-level authorization: checks ownership/visibility where needed.
  - Residents can only view their own service orders and billing data.
  - Listing edits are restricted to listing owner or manager.

## Core Backend Domains
### Auth
- Register/login/me endpoints.
- User profile includes role and optional shipping/mailing addresses.

### Resident Self-Service
- Resident-only profile read and address update endpoints.

### Listings
- Marketplace-style listings with draft/publish statuses.
- Multipart media upload support with content/size validation.
- Bulk status updates for manager workflows.

### Service Orders
- Residents create orders.
- Dispatcher/manager/admin update status.
- Status changes write audit history rows with timestamp, actor, and optional note.

### Billing
- Staff create billing records.
- Residents can upload payment proof for their own records.
- Statement download supports JSON/PDF formats.
- Refund request flow records resident credit requests.

### Homepage Configuration
- Dynamic homepage config with live/staged sections.
- Preview and rollout flags for controlled content release.
- Config writes are restricted to privileged roles in service logic.

## Data Modeling Notes
- Enum-driven states are centralized in `models/enums.py`:
  - Listing: `draft`, `published`, `unpublished`
  - Service order: `pending`, `in_progress`, `completed`
  - Billing: `pending`, `paid`, `overdue`, `refunded`
- Relationships support:
  - Listing -> media items
  - Service order -> status history
  - Billing record -> payment/refund evidence

## Logging
Standard Python logging is configured in `app/core/config.py` via `configure_logging()`.
Critical events are logged in auth, listing, and billing services/routers using `info`, `warning`, and `error` levels.

## Testing Strategy
- `unit_tests/`: service-level behavior and validation.
- `API_tests/`: end-to-end HTTP behavior and role/object authorization.
- `run_tests.sh`: single command to execute core unit and API suites with pass/fail summary.
