# Healiora Settings Integration (Patients & Doctors)

This guide explains how mobile and web clients (Flutter, Node, etc.) can integrate profile settings for Patients and Doctors. It is language-agnostic and focuses on HTTP endpoints, headers, and payloads.

## Base URL and Auth
- Base URL: `http://<YOUR_BACKEND_HOST>:8000`
- All endpoints below require a valid JWT access token in the Authorization header:
  - Header: `Authorization: Bearer <ACCESS_TOKEN>`

## Patients

### 1) Get my patient profile
- Method: GET
- Path: `/api/v1/patients/me`
- Auth: Required (role: patient)
- Response 200 (example):
```json
{
  "id": 12,
  "credential_id": 45,
  "email": "patient@example.com",
  "full_name": "Jane Doe",
  "gender": "female",
  "phone_number": "+1-202-555-0123",
  "age": 30,
  "emergency_contact": "+1-202-555-0199",
  "created_at": "2025-01-22T12:34:56.000Z"
}
```

### 2) Update my patient profile
- Method: PUT
- Path: `/api/v1/patients/update-profile`
- Auth: Required (role: patient)
- Body (any subset; all fields optional):
```json
{
  "full_name": "Jane Doe",
  "age": 31,
  "phone_number": "+1-202-555-0123",
  "emergency_contact": "+1-202-555-0199",
  "gender": "female"
}
```
- Response 200: Updated patient object (same shape as GET /me)

## Doctors

### 1) Get my doctor profile
- Method: GET
- Path: `/api/v1/doctors/me`
- Auth: Required (role: doctor)
- Response 200 (example):
```json
{
  "id": 7,
  "hospital_id": 3,
  "credential_id": 51,
  "name": "Dr. John Smith",
  "phone_number": "+1-202-555-0147",
  "email": "dr.smith@example.com",
  "address": "123 Medical Ave",
  "education": "MBBS, MD",
  "specialization": "Cardiology",
  "years_of_experience": 8
}
```

### 2) Update my doctor profile
- Method: PUT
- Path: `/api/v1/doctors/me`
- Auth: Required (role: doctor)
- Body (any subset; all fields optional):
```json
{
  "name": "Dr. John Smith",
  "phone_number": "+1-202-555-0147",
  "address": "123 Medical Ave",
  "education": "MBBS, MD",
  "specialization": "Cardiology",
  "years_of_experience": 9
}
```
- Response 200: Updated doctor object (same shape as GET /me)

## Status/Assignments (context)
- Resource availability is inferred from patient assignments, not directly set via a settings button.
- Related endpoints exist under `/api/v1/patient-assignments/` (e.g., `PUT /{assignment_id}/status`).

## Request Template (language-agnostic)
- GET
```
GET {BASE_URL}{PATH}
Headers:
  Authorization: Bearer {TOKEN}
  Content-Type: application/json
```
- PUT (with body)
```
PUT {BASE_URL}{PATH}
Headers:
  Authorization: Bearer {TOKEN}
  Content-Type: application/json
Body:
  { JSON payload with only fields you want to update }
```

## Error Handling
- 401 Unauthorized: Missing/invalid token
- 403 Forbidden: Wrong role (e.g., non-patient hitting patient settings)
- 404 Not Found: Profile not found for current credential
- 400 Bad Request: Validation errors
- 500 Server Error: Unexpected server failure

Error responses follow:
```json
{ "detail": "<error message>" }
```

## Minimal Client Examples (pseudo-code)

- Patient: fetch my profile
```
response = HTTP.GET(BASE_URL + "/api/v1/patients/me", headers={
  "Authorization": "Bearer " + token
})
patient = JSON.parse(response.body)
```

- Patient: update my profile
```
payload = { "full_name": "Jane Doe", "age": 31 }
response = HTTP.PUT(BASE_URL + "/api/v1/patients/update-profile", headers={
  "Authorization": "Bearer " + token,
  "Content-Type": "application/json"
}, body=JSON.stringify(payload))
updated = JSON.parse(response.body)
```

- Doctor: fetch my profile
```
response = HTTP.GET(BASE_URL + "/api/v1/doctors/me", headers={
  "Authorization": "Bearer " + token
})
doctor = JSON.parse(response.body)
```

- Doctor: update my profile
```
payload = { "address": "123 Medical Ave", "years_of_experience": 9 }
response = HTTP.PUT(BASE_URL + "/api/v1/doctors/me", headers={
  "Authorization": "Bearer " + token,
  "Content-Type": "application/json"
}, body=JSON.stringify(payload))
updated = JSON.parse(response.body)
```

## Notes for Flutter & Node Developers
- Flutter (Dio/http): supply the `Authorization` header on each call; serialize JSON body; handle 401/403.
- Node (fetch/axios): same pattern; ensure base URL and token are configurable via env.
- Always send only the fields you want to update (partial updates supported via PUT with optional fields).

---
If you need additional fields included in the settings, add them to the Patient/Doctor models and expose via the above endpoints. 