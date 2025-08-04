# Universal Login System

This document explains the universal login system that handles authentication for patients, doctors, and ambulances.

## Overview

The universal login system allows users to login with their email and password, and the system automatically detects their role and returns the appropriate JWT token. This enables role-based interface rendering on the frontend.

## API Endpoint

### Universal Login
**Endpoint**: `POST /credential/login`

**Purpose**: Authenticate users (patients, doctors, ambulances, hospitals) and return role-based JWT token.

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "patient",
    "user_id": 1
}
```

## Supported Roles

- **patient**: Patient users
- **doctor**: Doctor users  
- **ambulance**: Ambulance driver users
- **hospital**: Hospital admin users

## Frontend Implementation

### 1. Login Flow
```javascript
// Login user
const loginResponse = await fetch('/credential/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
    })
});

const { access_token, role, user_id } = await loginResponse.json();

// Store token and role
localStorage.setItem('token', access_token);
localStorage.setItem('userRole', role);
localStorage.setItem('userId', user_id);
```

### 2. Role-Based Interface Rendering
```javascript
// Check user role and show appropriate interface
const userRole = localStorage.getItem('userRole');

switch(userRole) {
    case 'patient':
        // Show patient dashboard
        showPatientInterface();
        break;
    case 'doctor':
        // Show doctor dashboard
        showDoctorInterface();
        break;
    case 'ambulance':
        // Show ambulance driver interface
        showAmbulanceInterface();
        break;
    case 'hospital':
        // Show hospital admin interface
        showHospitalInterface();
        break;
    default:
        // Show error or redirect to login
        showError('Invalid user role');
}
```

### 3. Protected Routes
```javascript
// Check if user is authenticated and has correct role
function requireAuth(requiredRole) {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');
    
    if (!token) {
        redirectToLogin();
        return false;
    }
    
    if (requiredRole && userRole !== requiredRole) {
        redirectToUnauthorized();
        return false;
    }
    
    return true;
}

// Usage in components
if (requireAuth('patient')) {
    // Show patient-specific content
}
```

## Error Handling

### 401 Unauthorized
- Invalid email or password
- User not found

### 403 Forbidden
- Invalid user role
- User role not in allowed list

### 404 Not Found
- User profile not found for the given role

## Security Features

1. **Password Verification**: Uses secure password hashing
2. **Role Validation**: Ensures user has valid role
3. **Profile Verification**: Checks if user profile exists for the role
4. **JWT Token**: Secure token-based authentication
5. **Role-Based Access**: Token contains user role for authorization

## Database Structure

### Credential Model
- `id`: Primary key
- `email`: User email (unique)
- `password`: Hashed password
- `role`: User role (patient/doctor/ambulance/hospital)
- `is_active`: Account status

### Profile Models
- **Patient**: Linked via `credential_id`
- **Doctor**: Linked via `credential_id`  
- **Ambulance**: Linked via `credential_id`
- **Hospital**: Linked via `credential_id`

## Usage Examples

### Patient Login
```bash
curl -X POST "http://localhost:8000/credential/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "patient@example.com", "password": "password123"}'
```

### Doctor Login
```bash
curl -X POST "http://localhost:8000/credential/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "password123"}'
```

### Ambulance Login
```bash
curl -X POST "http://localhost:8000/credential/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "ambulance@example.com", "password": "password123"}'
```

## Benefits

1. **Single Login Endpoint**: One endpoint handles all user types
2. **Role Detection**: Automatic role detection from database
3. **Frontend Flexibility**: Easy to implement role-based UI
4. **Security**: Proper authentication and authorization
5. **Scalability**: Easy to add new user roles 