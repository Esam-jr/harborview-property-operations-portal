# HarborView API Specification

Base URL: `http://localhost:8000/api/v1`

Auth scheme: `Authorization: Bearer <access_token>` for all protected endpoints.

## Health

### GET `/health/`
Response `200`:
```json
{ "status": "ok" }
```

## Auth

### POST `/auth/register`
Request:
```json
{
  "username": "resident1",
  "password": "strong-password",
  "role": "resident",
  "shipping_address": "Optional",
  "mailing_address": "Optional"
}
```
Response `201` (`UserRead`):
```json
{
  "id": 1,
  "username": "resident1",
  "role": "resident",
  "shipping_address": "Optional",
  "mailing_address": "Optional"
}
```

### POST `/auth/login`
Request:
```json
{
  "username": "resident1",
  "password": "strong-password"
}
```
Response `200`:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### GET `/auth/me`
Response `200` (`AuthenticatedUser`):
```json
{
  "username": "resident1",
  "role": "resident",
  "shipping_address": "Optional",
  "mailing_address": "Optional"
}
```

## Protected

### GET `/protected/me`
Response `200`:
```json
{
  "message": "Access granted",
  "user": {
    "username": "resident1",
    "role": "resident",
    "shipping_address": "Optional",
    "mailing_address": "Optional"
  },
  "timestamp": "2026-03-28T10:00:00Z"
}
```

## Resident

### GET `/resident/profile`
Role: `resident` only.

Response `200`:
```json
{
  "id": 1,
  "username": "resident1",
  "role": "resident",
  "shipping_address": "Address A",
  "mailing_address": "Address B"
}
```

### PUT `/resident/address`
Role: `resident` only.

Request:
```json
{
  "shipping_address": "New shipping address",
  "mailing_address": "New mailing address"
}
```
Response `200`: same shape as `/resident/profile`.

## Listings

### POST `/listings`
Role: `manager` only.  
Content type: `multipart/form-data`

Form fields:
- `title` (string, required)
- `description` (string, required)
- `status` (`draft | published | unpublished`, optional; default `draft`)
- `price_amount` (decimal, optional)
- `files` (file[], optional; JPG/PNG up to 10MB, MP4 up to 200MB)

Response `200` (`ListingRead`):
```json
{
  "id": 10,
  "owner_user_id": 2,
  "title": "Garage Sale",
  "description": "Saturday 9 AM",
  "price_amount": 25.0,
  "status": "draft",
  "media_items": []
}
```

### PUT `/listings/{listing_id}`
Role: owner or manager.  
Content type: `multipart/form-data`

Updatable form fields: `title`, `description`, `status`, `price_amount`, `files`.

Response `200`: `ListingRead`.

### PUT `/listings/{listing_id}/publish`
Role: owner or manager.

Response `200`: `ListingRead` with `status: "published"`.

### GET `/listings`
Query params:
- `status` (optional)
- `owner_user_id` (optional)

Response `200`: `ListingRead[]`.

### PATCH `/listings/bulk-update`
Role: `manager` only.

Request:
```json
{
  "ids": [1, 2, 3],
  "status": "published"
}
```
Response `200`:
```json
{
  "updated_count": 3,
  "status": "published"
}
```

## Service Orders

### POST `/orders`
Role: `resident` only.

Request:
```json
{
  "title": "Leaking sink",
  "description": "Water under cabinet",
  "due_date": "2026-03-30T08:00:00Z"
}
```
Response `201` (`OrderRead`) includes current status and `status_history`.

### GET `/orders`
Roles: all authenticated users.

Query params:
- `assigned_only` (boolean, optional; default `false`)

Behavior:
- Residents see only their own orders.
- Staff roles can view broader order sets.

Response `200`: `OrderRead[]`.

### GET `/orders/{order_id}`
Object-level auth enforced.

Response `200`: `OrderRead`.

### PUT `/orders/{order_id}/status`
### PATCH `/orders/{order_id}/status`
Roles: `dispatcher`, `manager`, or `admin`.

Request:
```json
{
  "status": "in_progress",
  "assigned_to_user_id": 5,
  "note": "Technician assigned and notified"
}
```
Response `200`: `OrderRead` (with appended status history entry).

## Billing

### POST `/billing`
Roles: `admin`, `manager`, `clerk`.

Request:
```json
{
  "resident_user_id": 1,
  "amount_due": 125.50,
  "due_date": "2026-04-01",
  "notes": "Monthly HOA dues"
}
```
Response `201` (`BillingRead`):
```json
{
  "id": 22,
  "resident_user_id": 1,
  "reference_code": "BILL-2026-00022",
  "amount_due": 125.5,
  "due_date": "2026-04-01",
  "status": "pending",
  "notes": "Monthly HOA dues"
}
```

### GET `/billing`
Roles: `admin`, `manager`, `clerk`, `resident`.

Response `200`: `BillingRead[]` (residents are restricted to their own records).

### GET `/billing/{billing_id}/statement?format={json|pdf}`
Roles: `admin`, `manager`, `clerk`, `resident`.  
Object-level auth enforced for residents.

Response `200`:
- JSON statement object when `format=json`
- PDF file response when `format=pdf`

### POST `/billing/{billing_id}/upload-proof`
Roles: `resident`, `clerk`, `manager`, `admin`.  
Content type: `multipart/form-data`

Form fields:
- `payment_method` (`check | money_order`)
- `amount` (decimal > 0)
- `payment_date` (date)
- `reference_number` (optional)
- `proof_file` (required; JPG/PNG up to 10MB)

Response `200`:
```json
{
  "evidence_id": 101,
  "billing_id": 22,
  "file_name": "receipt.png",
  "file_mime_type": "image/png",
  "file_size_bytes": 45678,
  "payment_method": "check"
}
```

### POST `/billing/{billing_id}/refund`
Roles: `resident`, `clerk`, `manager`, `admin`.

Request:
```json
{
  "amount": 25.0,
  "reason": "Duplicate payment"
}
```
Response `200`:
```json
{
  "billing_id": 22,
  "credit_amount": 25.0,
  "status": "refunded",
  "message": "Refund requested as resident credit"
}
```

## Homepage

### GET `/homepage`
Returns effective homepage content for current user.

Response `200`:
```json
{
  "sections": {
    "carousel_panels": [],
    "recommended_tiles": [],
    "announcement_banners": []
  },
  "source": "live",
  "preview_enabled": false,
  "rollout_enabled": false,
  "rollout_percentage": 10,
  "full_enablement": false
}
```

### GET `/homepage/config`
Privileged access enforced in service layer.

Response `200`:
```json
{
  "live": {
    "carousel_panels": [],
    "recommended_tiles": [],
    "announcement_banners": []
  },
  "staged": {
    "carousel_panels": [],
    "recommended_tiles": [],
    "announcement_banners": []
  },
  "preview_enabled": false,
  "rollout_enabled": false,
  "rollout_percentage": 10,
  "full_enablement": false
}
```

### PUT `/homepage/config`
Privileged access enforced in service layer.

Request:
```json
{
  "staged": {
    "carousel_panels": [],
    "recommended_tiles": [],
    "announcement_banners": []
  },
  "preview_enabled": true,
  "rollout_enabled": true,
  "rollout_percentage": 50,
  "full_enablement": false
}
```
Response `200`: same shape as `GET /homepage/config`.

## Common Error Responses
- `400`: invalid payload/business rule violation
- `401`: invalid/missing authentication
- `403`: role or object-level authorization failure
- `404`: resource not found
- `422`: schema validation failure
