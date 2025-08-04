# Admin Login System

This document describes the admin login functionality that has been implemented in the Healiora backend system.

## Overview

The admin login system provides secure authentication for users with admin privileges. Only users with the role "admin" can successfully authenticate through the admin login endpoints.

## Features

### 🔐 Security Features
- **Role-based Access Control**: Only users with `role="admin"` can login
- **Password Verification**: Uses bcrypt for secure password hashing
- **JWT Token Generation**: Secure token-based authentication
- **Account Status Verification**: Checks if the account is active (`is_active=True`)
- **Input Validation**: Email format validation and required field checks

### 🛡️ Error Handling
- **401 Unauthorized**: Invalid email/password or deactivated account
- **403 Forbidden**: User exists but doesn't have admin role
- **500 Internal Server Error**: Server-side errors during login process

## API Endpoints

### 1. Admin Login
```
POST /api/v1/admin/login
```

**Request Body:**
```json
{
  "email": "admin@healiora.com",
  "password": "admin123"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "role": "admin",
  "user_id": 1,
  "message": "Admin login successful"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Invalid email or password"
}
```

**Response (Error - 403):**
```json
{
  "detail": "Access denied. Admin privileges required."
}
```

### 2. Get Admin Profile
```
GET /api/v1/admin/me
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Success - 200):**
```json
{
  "id": 1,
  "email": "admin@healiora.com",
  "role": "admin",
  "is_active": true
}
```

### 3. Verify Admin Status
```
GET /api/v1/admin/verify
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Success - 200):**
```json
{
  "is_admin": true,
  "user_id": 1,
  "email": "admin@healiora.com",
  "role": "admin",
  "message": "Admin access verified"
}
```

## Implementation Details

### Service Layer (`app/services/admin.py`)

The admin service contains the core business logic:

- `admin_login()`: Main login function with role verification
- `get_admin_by_id()`: Get admin user by ID
- `get_admin_by_email()`: Get admin user by email
- `verify_admin_access()`: Verify if user has admin privileges

### API Layer (`app/api/v1/admin.py`)

The API layer provides HTTP endpoints:

- `admin_login_endpoint()`: Handles POST /admin/login
- `get_admin_profile()`: Handles GET /admin/me
- `verify_admin_status()`: Handles GET /admin/verify

### Schema Layer (`app/schemas/admin.py`)

Pydantic models for request/response validation:

- `AdminLoginRequest`: Login request schema
- `AdminLoginResponse`: Login response schema
- `AdminInfo`: Admin profile information schema

## Database Requirements

The system uses the existing `credentials` table with the following requirements:

```sql
-- Ensure admin user exists in credentials table
INSERT INTO credentials (email, password, role, is_active) 
VALUES ('admin@healiora.com', '$2b$12$...', 'admin', true);
```

## Usage Examples

### Python Requests Example
```python
import requests

# Admin login
response = requests.post(
    "http://localhost:8000/api/v1/admin/login",
    json={
        "email": "admin@healiora.com",
        "password": "admin123"
    }
)

if response.status_code == 200:
    token = response.json()["access_token"]
    
    # Use token for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(
        "http://localhost:8000/api/v1/admin/me",
        headers=headers
    )
    print(profile_response.json())
```

### cURL Example
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@healiora.com", "password": "admin123"}'

# Get profile (replace TOKEN with actual token)
curl -X GET "http://localhost:8000/api/v1/admin/me" \
  -H "Authorization: Bearer TOKEN"
```

## Testing

Run the test script to verify the admin login functionality:

```bash
python test_admin_login.py
```

The test script includes:
- Valid admin login test
- Non-admin user rejection test
- Invalid credentials test

## Security Considerations

1. **Password Security**: Passwords are hashed using bcrypt
2. **Token Security**: JWT tokens include user ID and role information
3. **Role Verification**: Multiple layers of role checking
4. **Account Status**: Inactive accounts are rejected
5. **Input Validation**: Email format and required field validation

## Integration with Existing System

The admin login system integrates seamlessly with the existing authentication system:

- Uses the same `credentials` table
- Compatible with existing JWT token system
- Follows the same security patterns as other login endpoints
- Uses the same middleware for authentication

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 401 | Invalid credentials or deactivated account |
| 403 | User exists but doesn't have admin role |
| 500 | Internal server error |

## Future Enhancements

Potential improvements for the admin system:

1. **Admin User Management**: CRUD operations for admin users
2. **Role Hierarchy**: Multiple admin roles (super admin, regular admin)
3. **Audit Logging**: Track admin actions
4. **Two-Factor Authentication**: Additional security layer
5. **Session Management**: Admin session tracking and management 