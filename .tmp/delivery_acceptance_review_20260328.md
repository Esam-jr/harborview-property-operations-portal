# HarborView Property Operations Portal - Delivery Acceptance / Project Architecture Review

Date: 2026-03-28
Scope: `C:\Users\hp\Desktop\My projects\harborview-property-operations-portal`
Acceptance benchmark: user-provided criteria (1.x, 2.x, 3.x, 4.x, 5.x, 6.x, 10.x)

## Environment Restriction Notes / Verification Boundary
- `python -m pytest unit_tests API_tests -v` failed because `python` is not available in the current shell (`CommandNotFoundException`).
- `py -m pytest unit_tests API_tests -v` failed because `py` is not available in the current shell.
- `bash run_tests.sh` failed with Windows Bash access denial (`E_ACCESSDENIED`).
- Per requirement, these are environment/tooling restrictions, not project defects.

Repro commands:
1. `cd "C:\Users\hp\Desktop\My projects\harborview-property-operations-portal"`
2. `python -m pytest unit_tests API_tests -v`
3. `py -m pytest unit_tests API_tests -v`
4. `bash run_tests.sh`

Current confirmable boundary:
- Static architecture/implementation compliance is confirmable from code and docs.
- Runtime pass/fail of tests and full live startup are unconfirmed in this environment.

---

## 1. Mandatory Thresholds

### 1.1 Deliverable can actually run and be verified

#### 1.1.1 Clear startup/operation instructions
- Conclusion: **Pass**
- Reason (basis): README provides startup command, service URLs, optional offline mode, and test commands.
- Evidence:
  - `repo/README.md:11-23`
  - `repo/README.md:25-41`
  - `repo/README.md:43-60`
- Reproducible verification:
  1. `cd repo`
  2. `docker compose up --build`
  3. Expect frontend on `http://localhost:5173`, backend on `http://localhost:8000`.

#### 1.1.2 Can start/run without modifying core code
- Conclusion: **Partially Pass**
- Reason (basis): Deployment files are present and coherent, but this review could not execute runtime due environment restrictions (no Python launcher and no runnable bash; Docker intentionally not started per instruction).
- Evidence:
  - `repo/docker-compose.yml:1-48`
  - `repo/backend/Dockerfile:1-20`
  - `repo/frontend/Dockerfile:1-18`
  - `run_tests.sh:1-46`
- Reproducible verification:
  1. `cd repo && docker compose up --build`
  2. `cd .. && python -m pytest unit_tests API_tests -v`
  3. Expect all services and tests to run without source edits.

#### 1.1.3 Runtime result basically matches delivery description
- Conclusion: **Partially Pass**
- Reason (basis): Core modules align with prompt (auth, listings, orders, billing, homepage config, PWA), but staff-role usability out-of-box is blocked by missing documented bootstrap admin creation.
- Evidence:
  - Resident-only registration in API: `repo/backend/app/routers/auth.py:31-37`
  - Staff creation requires logged-in admin: `repo/backend/app/routers/auth.py:43-59`
  - No admin bootstrap in README run flow: `repo/README.md:11-23`
  - Seed utility exists but not in delivery run steps: `repo/backend/seed.py:21-45`
- Reproducible verification:
  1. Start backend with empty DB.
  2. Attempt `POST /api/v1/auth/register` with role `manager` (role ignored to resident pathway).
  3. Attempt `POST /api/v1/auth/staff` without admin token -> expect 401/403.
  4. Staff-role login path remains unavailable unless DB is manually seeded.

### 1.3 Severe deviation from Prompt theme

#### 1.3.1 Business goal/scenario alignment
- Conclusion: **Pass**
- Reason (basis): The implementation is centered on HOA/multifamily operations across billing, listings, service orders, resident self-service, and admin homepage controls.
- Evidence:
  - Billing module: `repo/backend/app/routers/billing.py:32-147`
  - Listings module: `repo/backend/app/routers/listings.py:39-128`
  - Orders module: `repo/backend/app/routers/orders.py:30-95`
  - Resident self-service: `repo/backend/app/routers/resident.py:14-58`
  - Homepage config/rollout: `repo/backend/app/services/homepage_service.py:35-201`
- Reproducible verification:
  1. Authenticate each role and call corresponding endpoints.
  2. Confirm module behavior aligns to role responsibilities.

#### 1.3.2 Core problem replaced/weakened/ignored
- Conclusion: **Partially Pass**
- Reason (basis): Theme is preserved, but “all roles sign in and use role navigation” is weakened at bootstrap because staff accounts depend on pre-existing admin not documented in startup path.
- Evidence:
  - `repo/backend/app/routers/auth.py:43-59`
  - `repo/README.md:11-23`
- Reproducible verification:
  1. Fresh DB run.
  2. Attempt staff onboarding without seeded admin.
  3. Observe blocked staff activation.

---

## 2. Delivery Completeness

### 2.1 Core prompt requirements implemented

#### 2.1.1 Local username/password auth and role navigation (admin/manager/clerk/dispatcher/resident)
- Conclusion: **Partially Pass**
- Reason (basis): Authentication and route-role guards are implemented, but staff-role account bootstrap is not fully deliverable out-of-box.
- Evidence:
  - JWT login/profile: `repo/backend/app/routers/auth.py:88-110`
  - Token auth dependency: `repo/backend/app/api/deps/auth.py:14-31`
  - Frontend route role guards: `repo/frontend/src/router/index.js:59-75`
  - Role set: `repo/backend/app/models/enums.py:4-9`
- Reproducible verification:
  1. Login via `/api/v1/auth/login`.
  2. Navigate protected routes; unauthorized role should redirect/deny.

#### 2.1.2 Resident address maintenance
- Conclusion: **Pass**
- Reason (basis): Resident profile and address update endpoints + frontend form are implemented.
- Evidence:
  - API: `repo/backend/app/routers/resident.py:14-58`
  - Service: `repo/backend/app/services/resident_service.py:17-42`
  - UI: `repo/frontend/src/pages/ResidentDashboardPage.vue:10-25`
- Reproducible verification:
  1. Resident login.
  2. `PUT /api/v1/resident/address` with shipping/mailing values.
  3. `GET /api/v1/resident/profile` should reflect update.

#### 2.1.3 Statements view/download + payment evidence + refund-as-credit
- Conclusion: **Pass**
- Reason (basis): JSON/PDF statement retrieval, payment proof upload (JPG/PNG), and refund request adjusting billed amount/status are implemented.
- Evidence:
  - Billing routes: `repo/backend/app/routers/billing.py:64-147`
  - Statement formats: `repo/backend/app/services/billing_service.py:241-272`
  - Proof upload & validation: `repo/backend/app/services/billing_service.py:93-169`, `repo/backend/app/services/billing_file_validation.py:15-27`
  - Refund credit behavior: `repo/backend/app/services/billing_service.py:172-239`
- Reproducible verification:
  1. Create billing record as staff.
  2. Upload proof as resident (`/upload-proof`).
  3. Request refund (`/refund`).
  4. Download statement with `format=json` and `format=pdf`.

#### 2.1.4 Service order status badges + timestamped milestones
- Conclusion: **Pass**
- Reason (basis): Status history rows are persisted with timestamp/note/actor and rendered with badges + formatted timestamps in resident UI.
- Evidence:
  - History write: `repo/backend/app/services/service_order_service.py:120-125`
  - Status history schema includes changed_at: `repo/backend/app/schemas/service_order.py:20-29`
  - Resident UI badges/timestamps: `repo/frontend/src/pages/ResidentDashboardPage.vue:150-154`
- Reproducible verification:
  1. Resident creates order.
  2. Manager/dispatcher updates status.
  3. Resident dashboard should show milestone timeline.

#### 2.1.5 Listings: draft/edit/publish-unpublish/bulk status/media upload validation
- Conclusion: **Pass**
- Reason (basis): Listing CRUD + status transitions + bulk update + file validations (JPG/PNG<=10MB, MP4<=200MB) exist in backend and immediate frontend feedback before submit.
- Evidence:
  - Create/edit/publish/bulk endpoints: `repo/backend/app/routers/listings.py:39-128`
  - Backend media limits: `repo/backend/app/services/file_validation.py:16-39`, `repo/backend/app/core/config.py:27-28`
  - Frontend immediate validation: `repo/frontend/src/pages/ListingsPage.vue:180-204`, `repo/frontend/src/pages/ListingsPage.vue:206-216`
- Reproducible verification:
  1. Manager uploads valid and invalid files in Listings UI.
  2. Expect client-side error for unsupported/oversized files.
  3. Verify server rejects unsupported formats via API.

#### 2.1.6 Admin homepage modular sections + preview + 10% controlled rollout + full enablement
- Conclusion: **Pass**
- Reason (basis): Staged/live sections, preview flag, rollout flag, configurable percentage defaulting 10, and full enablement propagation are implemented with admin authorization.
- Evidence:
  - Config model defaults: `repo/backend/app/models/homepage_config.py:26-29`
  - Update + full enablement copy: `repo/backend/app/services/homepage_service.py:45-54`
  - Rollout bucket logic for staff: `repo/backend/app/services/homepage_service.py:195-200`
  - Admin-only config mutation: `repo/backend/app/services/homepage_service.py:204-209`
  - Admin UI config editor: `repo/frontend/src/pages/HomePage.vue:40-84`
- Reproducible verification:
  1. Admin updates staged sections and flags.
  2. Compare `/api/v1/homepage` response for multiple staff users.
  3. Confirm ~bucketed rollout behavior and full enablement switch.

#### 2.1.7 Optional offline-capable installable mode
- Conclusion: **Pass**
- Reason (basis): PWA initialization is feature-flagged and supports install prompt/service worker registration.
- Evidence:
  - Feature flag + SW registration: `repo/frontend/src/services/pwaService.js:3-47`
  - Install handling: `repo/frontend/src/services/pwaService.js:48-68`
  - Bootstrap call: `repo/frontend/src/main.js:5-8`
- Reproducible verification:
  1. Set `VITE_ENABLE_OFFLINE_MODE=true`.
  2. Build and open app in supported browser.
  3. Verify install prompt and offline status indicator.

### 2.2 Basic delivery form (project-level completeness)

#### 2.2.1 Complete project structure/docs present
- Conclusion: **Pass**
- Reason (basis): Multi-module frontend/backend architecture, tests, docs, and compose deployment are all present.
- Evidence:
  - README/docs: `repo/README.md:1-73`, `docs/design.md:1-83`, `docs/api-spec.md:1-372`
  - Source layout: `repo/backend/app/*`, `repo/frontend/src/*`
  - Tests: `unit_tests/*`, `API_tests/*`
- Reproducible verification:
  1. `rg --files`
  2. Confirm expected directories/files exist.

#### 2.2.2 Mock/hardcode replacing real logic without explanation
- Conclusion: **Partially Pass**
- Reason (basis): Statement PDF is intentionally mock text (`application/pdf` response). This is acceptable per rule (payment mock not issue), but should be documented as non-final generation behavior.
- Evidence:
  - Mock PDF assembly: `repo/backend/app/services/billing_service.py:263-271`
  - API spec currently presents it as PDF response but does not clearly state mock implementation: `docs/api-spec.md:253-260`
- Reproducible verification:
  1. Call `GET /api/v1/billing/{id}/statement?format=pdf`.
  2. Observe text-based payload returned as pdf MIME.

---

## 3. Engineering and Architecture Quality

### 3.1 Reasonable engineering structure and module division
- Conclusion: **Pass**
- Reason (basis): Clear layered separation of routers/services/models/schemas/deps/db; modules are coherent by domain.
- Evidence:
  - Declared architecture: `docs/design.md:4-10`
  - Router assembly: `repo/backend/app/routers/__init__.py:5-13`
  - Service-layer logic examples: `repo/backend/app/services/listing_service.py:23-269`, `repo/backend/app/services/billing_service.py:25-293`
- Reproducible verification:
  1. Trace request path from router -> service -> model/schema in each domain.

### 3.2 Maintainability/extensibility awareness
- Conclusion: **Pass**
- Reason (basis): Enum centralization, schema contracts, reusable auth dependency, and service-level validations support extension.
- Evidence:
  - Enums: `repo/backend/app/models/enums.py:4-48`
  - Shared auth dependency: `repo/backend/app/api/deps/auth.py:14-31`
  - Validation components: `repo/backend/app/services/file_validation.py:16-39`, `repo/backend/app/schemas/homepage.py:11-21`
- Reproducible verification:
  1. Add new enum value/role and trace required updates by module boundaries.

---

## 4. Engineering Details and Professionalism

### 4.1 Error handling / logging / validation / interface quality

#### 4.1.1 Error handling reliability and friendliness
- Conclusion: **Pass**
- Reason (basis): Uses HTTPException with appropriate statuses for validation, authz, not found, and server errors.
- Evidence:
  - Auth errors: `repo/backend/app/routers/auth.py:28-30`, `repo/backend/app/routers/auth.py:92-94`
  - Listings validation/404/500: `repo/backend/app/services/listing_service.py:29-39`, `repo/backend/app/services/listing_service.py:193-223`
  - Orders errors: `repo/backend/app/services/service_order_service.py:86-116`
  - Billing errors: `repo/backend/app/services/billing_service.py:106-167`, `repo/backend/app/services/billing_service.py:190-236`
- Reproducible verification:
  1. Submit invalid payloads and unauthorized requests.
  2. Confirm 4xx/5xx semantics.

#### 4.1.2 Logging for diagnosis
- Conclusion: **Pass**
- Reason (basis): Structured logging helper and domain logs at info/warning/error levels.
- Evidence:
  - Logging config: `repo/backend/app/core/config.py:76-84`
  - Auth logging: `repo/backend/app/routers/auth.py:28`, `repo/backend/app/routers/auth.py:96-99`
  - Billing/listing logging: `repo/backend/app/services/billing_service.py:40-73`, `repo/backend/app/services/listing_service.py:66-87`
- Reproducible verification:
  1. Run API and trigger success/failure flows.
  2. Inspect logs for structured records.

#### 4.1.3 Input/boundary validation
- Conclusion: **Pass**
- Reason (basis): Pydantic and service-level validations cover lengths, types, ranges, file MIME/size constraints.
- Evidence:
  - Auth and resident fields: `repo/backend/app/schemas/auth.py:16-39`, `repo/backend/app/schemas/resident.py:14-16`
  - Listing constraints: `repo/backend/app/schemas/listing.py:20-33`
  - Billing constraints: `repo/backend/app/schemas/billing.py:9-47`
  - Media constraints: `repo/backend/app/services/file_validation.py:27-39`, `repo/backend/app/services/billing_file_validation.py:15-27`
- Reproducible verification:
  1. Send invalid values (negative amount, short title, bad MIME).
  2. Expect validation failure statuses.

### 4.2 Product-form vs demo-form
- Conclusion: **Partially Pass**
- Reason (basis): Overall app form is production-like, but missing documented staff bootstrap and use of default insecure JWT secret reduce production readiness.
- Evidence:
  - Product modules: `repo/frontend/src/pages/*.vue`, `repo/backend/app/routers/*.py`
  - JWT default secret placeholder: `repo/backend/app/core/config.py:18`
  - Staff bootstrap gap: `repo/backend/app/routers/auth.py:43-59`, `repo/README.md:11-23`
- Reproducible verification:
  1. Deploy with defaults and inspect auth security/staff onboarding behavior.

### Security Priority Audit (Authentication/Authorization/Isolation)

#### Authentication entry points
- Conclusion: **Partially Pass**
- Basis: JWT-based auth and password hashing are implemented, but default secret key is unsafe if not overridden.
- Evidence:
  - JWT creation/verification: `repo/backend/app/core/security.py:19-29`
  - Default key: `repo/backend/app/core/config.py:18`
  - Login endpoint: `repo/backend/app/routers/auth.py:88-99`
- Repro idea:
  1. Run production with default env.
  2. Secret remains known constant -> token forgery risk.

#### Route-level authorization
- Conclusion: **Pass**
- Basis: Role checks applied at listing/order/billing/homepage/resident routes.
- Evidence:
  - Listings manager gate: `repo/backend/app/routers/listings.py:21-26`
  - Orders status gate: `repo/backend/app/routers/orders.py:14-19`
  - Billing role gates: `repo/backend/app/routers/billing.py:24-42`
  - Homepage admin gate: `repo/backend/app/services/homepage_service.py:204-209`
- Repro idea:
  1. Call privileged endpoints with resident token.
  2. Expect 403.

#### Object-level authorization
- Conclusion: **Pass**
- Basis: Resident ownership checks exist for service orders and billing records.
- Evidence:
  - Orders object check: `repo/backend/app/routers/orders.py:22-27`
  - Billing record ownership: `repo/backend/app/services/billing_service.py:290-293`
  - Listing owner/manager edit gate: `repo/backend/app/routers/listings.py:29-36`
- Repro idea:
  1. Resident A request resident B order/billing resource.
  2. Expect 403.

#### Tenant/user data isolation
- Conclusion: **Pass (single-tenant scope)**
- Basis: Resident-scoped queries filter by authenticated user id.
- Evidence:
  - Orders list filter: `repo/backend/app/services/service_order_service.py:60-63`
  - Billing list filter: `repo/backend/app/services/billing_service.py:87-89`
- Repro idea:
  1. Log in as resident A and resident B.
  2. Compare list outputs.

#### Admin/debug interface protection
- Conclusion: **Pass**
- Basis: Staff provisioning is admin-only; homepage config is admin-only.
- Evidence:
  - Staff provision restriction: `repo/backend/app/routers/auth.py:49-59`
  - Homepage config admin requirement: `repo/backend/app/services/homepage_service.py:204-209`
- Repro idea:
  1. Manager token on `/auth/staff` or `/homepage/config` update.
  2. Expect 403.

---

## 5. Prompt Requirement Understanding and Fitness

### 5.1 Business goals/scenarios/implicit constraints fit
- Conclusion: **Partially Pass**
- Reason (basis): Most semantic requirements are addressed (operations portal, role UX, resident self-service, listings, orders, homepage rollout, offline mode). Main fitness gap is out-of-box staff activation path and production-secret hygiene.
- Evidence:
  - Feature breadth: `repo/backend/app/routers/__init__.py:6-13`, `repo/frontend/src/router/index.js:12-51`
  - Gap evidence: `repo/backend/app/routers/auth.py:43-59`, `repo/backend/app/core/config.py:18`
- Reproducible verification:
  1. Execute role-based flow scenarios by persona.
  2. Verify staff onboarding and secure env config before production.

---

## 6. Aesthetics (Frontend/full-stack applicable)

### 6.1 Visual/interaction appropriateness
- Conclusion: **Pass**
- Reason (basis): Distinct cards/tables/badges, responsive layout, coherent spacing/typography/colors, and loading/hover/disabled feedback are present.
- Evidence:
  - Shared visual system and responsive rules: `repo/frontend/src/assets/main.css:1-383`
  - Header/nav responsive behavior: `repo/frontend/src/components/AppHeader.vue:81-179`
  - Interactive states: `repo/frontend/src/assets/main.css:145-180`, `repo/frontend/src/pages/ListingsPage.vue:40-42`
- Reproducible verification:
  1. Open app on desktop and narrow viewport.
  2. Confirm responsive nav and visual consistency across modules.

Not Applicable notes:
- No custom image/illustration theme mismatch observed in static code (N/A for external media assets beyond icons).

---

## Separate Audit: Unit Tests / API Tests / Log Categorization

### Unit tests
- Conclusion: **Exists, but partial scope**
- Basis: Unit tests cover user service, listing field validation/ownership assignment, service order transitions, homepage admin gating; no dedicated billing service unit suite found.
- Evidence:
  - Present: `unit_tests/test_user_service.py`, `unit_tests/test_listing_service.py`, `unit_tests/test_service_order_service.py`, `unit_tests/test_homepage_service.py`
  - Missing file signal: no `unit_tests/test_billing_service.py` in repo file list.
- Executability: documented, but unconfirmed here due environment tooling limits.

### API/integration tests
- Conclusion: **Exists, good core auth/order/billing/listing coverage, but incomplete for homepage and several boundary paths**
- Evidence:
  - `API_tests/test_auth_api.py`
  - `API_tests/test_orders_api.py`
  - `API_tests/test_billing_api.py`
  - `API_tests/test_listings_api.py`
- Executability: documented, but unconfirmed here due environment tooling limits.

### Log printing categorization
- Conclusion: **Basic categorization present; sensitive-token/password leakage not observed in backend logs**
- Evidence:
  - Logger config levels/format: `repo/backend/app/core/config.py:70-84`
  - Domain log statements: `repo/backend/app/routers/auth.py:28-99`, `repo/backend/app/services/billing_service.py:40-73`
  - No direct token/password logging in backend code paths inspected.

---

## Issues (Prioritized)

### [Blocking] Missing documented staff bootstrap path prevents full role-based acceptance on fresh deployment
- Impact: Core prompt expectation (all roles sign in and use role navigation) cannot be achieved out-of-box in a clean environment.
- Evidence:
  - Resident-only registration path: `repo/backend/app/routers/auth.py:31-37`
  - Staff creation requires existing admin: `repo/backend/app/routers/auth.py:43-59`
  - README startup omits admin bootstrap/seed step: `repo/README.md:11-23`
- Minimal actionable suggestion:
  1. Add deterministic bootstrap admin flow (migration seed or env-driven first-admin creation).
  2. Document it in README startup steps.
  3. Add API test asserting staff provisioning works from clean initialization sequence.

### [High] Insecure default JWT secret key risks token forgery if deployed without override
- Impact: If default is used in production, attackers can mint valid tokens and bypass authentication.
- Evidence:
  - `repo/backend/app/core/config.py:18`
  - Token operations rely on this secret: `repo/backend/app/core/security.py:22`, `repo/backend/app/core/security.py:27`
- Minimal actionable suggestion:
  1. Remove insecure default; require non-empty env var in non-test environments.
  2. Fail startup when secret equals known placeholder.
  3. Add config validation test.

### [Medium] Test coverage gaps leave important regressions undetected despite possible green test runs
- Impact: Homepage rollout semantics, listing media edge paths, and pagination/filter/empty-state boundaries can regress unnoticed.
- Evidence:
  - No homepage API tests in `API_tests/`.
  - Listings API tests do not cover media size/type boundary exhaustively: `API_tests/test_listings_api.py:1-75`
  - No pagination/sorting coverage; list endpoints have no pagination params in routers.
- Minimal actionable suggestion:
  1. Add `API_tests/test_homepage_api.py` for preview/rollout/full enablement permutations.
  2. Add listing upload boundary tests (10MB/200MB edges + unsupported MIME).
  3. Add explicit empty-data and filter behavior tests for orders/billing/listings.

### [Low] Mock PDF behavior should be explicitly documented as non-final renderer
- Impact: Consumers may assume true PDF generation while implementation returns plain text bytes with PDF MIME.
- Evidence:
  - `repo/backend/app/services/billing_service.py:263-271`
  - `docs/api-spec.md:253-260`
- Minimal actionable suggestion:
  1. Document current behavior as mock/stub PDF generation.
  2. Add TODO marker for real PDF renderer integration path.

---

## Test Coverage Assessment (Static Audit)

### Test Overview
- Unit tests exist: `unit_tests/test_user_service.py`, `unit_tests/test_listing_service.py`, `unit_tests/test_service_order_service.py`, `unit_tests/test_homepage_service.py`.
- API/integration tests exist: `API_tests/test_auth_api.py`, `API_tests/test_orders_api.py`, `API_tests/test_billing_api.py`, `API_tests/test_listings_api.py`.
- Framework/entry:
  - Pytest usage in README and script: `repo/README.md:43-60`, `run_tests.sh:19-25`
  - FastAPI TestClient + SQLite fixtures: `conftest.py:41-84`
- README provides executable commands: yes (`repo/README.md:43-60`) (execution unconfirmed in this environment).

### Coverage Mapping Table
| Requirement / Risk Point | Corresponding Test Case (file:line) | Key Assertion / Fixture / Mock (file:line) | Coverage Judgment | Gap | Minimal Test Addition Suggestion |
|---|---|---|---|---|---|
| Auth happy path (register/login/protected) | `API_tests/test_auth_api.py:1-25` | `status_code==201/200`, token use on `/protected/me` | Sufficient | None major | Keep |
| Invalid credentials -> 401 | `API_tests/test_auth_api.py:27-36` | Explicit 401 assertion | Sufficient | None major | Keep |
| Unauthenticated access -> 401 | `API_tests/test_auth_api.py:83-85` | No token to protected route | Sufficient | None major | Keep |
| Staff provisioning authorization (admin-only) | Indirect in helper flows `API_tests/test_orders_api.py:13-38`, `API_tests/test_billing_api.py:18-44` | Admin token required to call `/auth/staff` | Basic Coverage | No direct negative case asserting non-admin denied | Add explicit `/auth/staff` non-admin 403 test |
| Route-level auth: listings manager-only | `API_tests/test_listings_api.py:26-41`, `:43-75` | Resident create/bulk update returns 403 | Sufficient | No clerk/dispatcher permutations | Add matrix test for all non-manager roles |
| Object-level auth: order ownership | `API_tests/test_orders_api.py:167-194` | Resident A denied on resident B order | Sufficient | None major | Keep |
| Object-level auth: billing ownership | `API_tests/test_billing_api.py:146-190`, `:233-272` | Resident denied for other resident statement | Sufficient | Duplicate overlap but acceptable | Keep |
| Resident billing list isolation | `API_tests/test_billing_api.py:138-144` | Resident list returns only own billed record | Basic Coverage | Single-record scenario only | Add multi-record mixed-owner list isolation test |
| Service order multi-step happy flow | `API_tests/test_orders_api.py:110-165` | Create->status update->history length/note asserts | Sufficient | None major | Keep |
| Service order invalid transition boundary | `unit_tests/test_service_order_service.py:25-47` | in_progress without assignment -> 400 | Sufficient | No API-level equivalent | Add API transition failure test |
| Listing field validation boundary | `unit_tests/test_listing_service.py:10-16` | Short title -> 422 | Basic Coverage | Missing description boundary and update path | Add title/description update validation cases |
| Listing media upload boundaries | None direct in unit/API | N/A | Missing | No tests for jpg/png/mp4 limits and invalid oversized files | Add listing media MIME/size tests |
| Billing proof invalid MIME | `API_tests/test_billing_api.py:192-231` | text/plain proof rejected | Basic Coverage | No explicit >10MB boundary test | Add max-size boundary tests |
| Homepage admin auth/update | `unit_tests/test_homepage_service.py:23-68` | Admin success, manager/resident 403 | Basic Coverage | No API-level tests; no rollout bucket verification | Add homepage API tests for preview/rollout/full enablement behavior |
| Controlled rollout semantics (10% staff) | None direct | N/A | Missing | No deterministic bucket behavior tests | Add deterministic user-id/username bucket tests |
| Pagination/sorting/filter boundaries | Minimal (listings list happy path) `API_tests/test_listings_api.py:19-24` | Basic list assert | Insufficient | No pagination/sorting tests; endpoints mostly unpaginated | Add filter/empty/extreme-result tests |
| 404 coverage for missing resources | `API_tests/test_orders_api.py:196-206` | Nonexistent order -> 404 | Basic Coverage | Billing/listing 404 paths not broadly tested | Add 404 tests for billing/listing operations |
| Conflict/duplicate behavior | Mostly auth duplicate username not directly tested | N/A | Insufficient | No explicit duplicate register/staff create API tests | Add duplicate username 400 tests |
| Logs and sensitive info leakage | Static code audit only | Logger statements include usernames/ids only | Basic Coverage | No tests asserting redaction/non-leak | Add tests (or lint rules) to prevent token/password logging |

### Security Coverage Audit
- Authentication: **Basic Coverage** (happy path + invalid password + no token tested). Missing secret-management test.
- Route Authorization: **Basic Coverage** (listings/orders/billing role checks partially covered).
- Object-level Authorization: **Sufficient for orders and billing** (resident cross-access denial tests present).
- Data Isolation: **Basic Coverage** (billing/order resident isolation tested in representative paths; more permutations needed).

### Mock/Stub Handling Assessment
- Payment-related mock/stub is present in statement PDF generation (text payload with `application/pdf`): `repo/backend/app/services/billing_service.py:263-271`.
- Activation condition: triggered when `format=pdf` (`repo/backend/app/services/billing_service.py:260-271`).
- Accidental deployment risk: medium documentation risk (appears production endpoint unless explicitly documented).
- Per rule: not treated as defect solely for being mock; documented as delivery clarity risk.

### Overall Static Test Sufficiency Judgment
- Conclusion: **Partially Pass**
- Basis boundary:
  - Covered well: core auth, key role gates, order lifecycle chain, critical object-level restrictions.
  - Under-covered/missing: homepage rollout semantics, listing media boundaries, broader negative/authz matrixes, and log-safety assertions.
  - Therefore tests may pass while severe defects still exist in rollout behavior, media validation edge cases, or production security configuration.

Minimal high-priority additions:
1. Homepage API tests for `preview_enabled`, `rollout_enabled`, `rollout_percentage`, `full_enablement` behavior across roles.
2. Listing media boundary tests for allowed/blocked MIME and exact size limits.
3. Auth configuration test enforcing non-placeholder JWT secret in production mode.
4. Staff bootstrap/first-admin initialization integration test from clean DB.

---

## Final Acceptance Verdict
- **Overall: Partially Pass**
- Rationale: Product architecture and core functional coverage are strong and prompt-aligned, but acceptance is blocked from full pass by out-of-box staff bootstrap gap and a high-severity JWT default-secret security risk, plus notable static test coverage blind spots.
