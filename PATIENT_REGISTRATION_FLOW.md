# Patient Registration Flow

This document explains the two-step patient registration process implemented in the Healiora backend.

## Overview

The patient registration process is divided into two steps:

1. **Step 1**: Initial registration with basic information
2. **Step 2**: Profile completion with additional details

## API Endpoints

### Step 1: Initial Registration
**Endpoint**: `POST /register`

**Purpose**: Create initial patient account with email, password, and full name.

**Request Body**:
```json
{
    "email": "patient@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
}
```

**Response**:
```json
{
    "id": 1,
    "credential_id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "gender": null,
    "phone_number": null,
    "age": null,
    "emergency_contact": null,
    "created_at": "2024-01-01T00:00:00"
}
```

### Step 2: Profile Completion (Two Options)

#### Option A: Complete Profile Immediately (No Auth Required)
**Endpoint**: `PUT /complete-profile/{patient_id}`

**Purpose**: Complete patient profile immediately after registration without needing to login.

**Request Body**:
```json
{
    "phone_number": "+1234567890",
    "age": 30,
    "gender": "male",
    "emergency_contact": "+1987654321"
}
```

**Response**:
```json
{
    "id": 1,
    "credential_id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "gender": "male",
    "phone_number": "+1234567890",
    "age": 30,
    "emergency_contact": "+1987654321",
    "created_at": "2024-01-01T00:00:00"
}
```

#### Option B: Complete Profile After Login (Auth Required)
**Endpoint**: `PUT /update-profile`

**Headers**: `Authorization: Bearer <jwt_token>`

**Purpose**: Complete patient profile after logging in.

**Request Body**:
```json
{
    "phone_number": "+1234567890",
    "age": 30,
    "gender": "male",
    "emergency_contact": "+1987654321"
}
```

## Database Structure

### Credential Model
- Stores email, password, and role
- One-to-one relationship with Patient

### Patient Model
- Stores patient-specific information
- Linked to Credential via credential_id
- Fields: full_name, gender, email, phone_number, age, emergency_contact

## Usage Flow

### Flow 1: Immediate Profile Completion (Recommended)
1. **Frontend Step 1**: 
   - User fills email, password, and full name
   - Calls `POST /register`
   - Receives patient object with ID

2. **Frontend Step 2**:
   - User immediately fills additional details form
   - Calls `PUT /complete-profile/{patient_id}` with the ID from step 1
   - Profile is completed without needing to login

### Flow 2: Profile Completion After Login
1. **Frontend Step 1**: 
   - User fills email, password, and full name
   - Calls `POST /register`
   - Receives success response

2. **Frontend Step 2**:
   - User logs in with email/password
   - Receives JWT token
   - User fills additional details form
   - Calls `PUT /update-profile` with JWT token
   - Profile is completed

## Authentication

- Step 1 doesn't require authentication
- Step 2 has two options:
  - **Option A**: No auth required (immediate completion)
  - **Option B**: JWT token required (after login)
- Token contains user_id and role="patient"

## Error Handling

- Email already exists: 400 Bad Request
- Invalid credentials: 401 Unauthorized
- Patient not found: 404 Not Found
- Server errors: 500 Internal Server Error

## Additional Endpoints

- `POST /login`: Patient login
- `GET /me`: Get current patient profile
- `GET /{patient_id}`: Admin endpoint to get any patient 