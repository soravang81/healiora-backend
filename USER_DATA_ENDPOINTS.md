# User Data Endpoints

This document explains the user data endpoints that allow fetching current user information from JWT tokens.

## Overview

These endpoints allow authenticated users to fetch their credential and profile data using their JWT token.

## API Endpoints

### 1. Get My Credential
**Endpoint**: `GET /credential/me`

**Purpose**: Get current user's basic credential information from JWT token.

**Headers**: `Authorization: Bearer <jwt_token>`

**Response**:
```json
{
    "id": 1,
    "role": "patient",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### 2. Get Comprehensive User Data
**Endpoint**: `GET /credential/user-data`

**Purpose**: Get comprehensive user data including credential and role-specific profile information.

**Headers**: `Authorization: Bearer <jwt_token>`

**Response Examples**:

#### Patient Response
```json
{
    "id": 1,
    "email": "patient@example.com",
    "role": "patient",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "profile_data": {
        "full_name": "John Doe",
        "gender": "male",
        "phone_number": "+1234567890",
        "age": 30,
        "emergency_contact": "+1987654321"
    }
}
```

#### Doctor Response
```json
{
    "id": 2,
    "email": "doctor@example.com",
    "role": "doctor",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "profile_data": {
        "name": "Dr. Jane Smith",
        "phone_number": "+1234567890",
        "address": "123 Medical Center Dr",
        "education": "MD, Cardiology",
        "specialization": "Cardiology",
        "years_of_experience": 10
    }
}
```

#### Ambulance Response
```json
{
    "id": 3,
    "email": "ambulance@example.com",
    "role": "ambulance",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "profile_data": {
        "driver_name": "Mike Johnson",
        "driver_phone": "+1234567890",
        "ambulance_number": "AMB-001",
        "vehicle_type": "Emergency Ambulance"
    }
}
```

## Frontend Implementation

### 1. Get Basic Credential Data
```javascript
// Get basic user credential data
const response = await fetch('/credential/me', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});

const credentialData = await response.json();
console.log('User ID:', credentialData.id);
console.log('User Role:', credentialData.role);
```

### 2. Get Comprehensive User Data
```javascript
// Get comprehensive user data with profile information
const response = await fetch('/credential/user-data', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});

const userData = await response.json();
console.log('User Email:', userData.email);
console.log('User Role:', userData.role);
console.log('Profile Data:', userData.profile_data);

// Use profile data based on role
if (userData.role === 'patient') {
    console.log('Patient Name:', userData.profile_data.full_name);
    console.log('Patient Age:', userData.profile_data.age);
} else if (userData.role === 'doctor') {
    console.log('Doctor Name:', userData.profile_data.name);
    console.log('Specialization:', userData.profile_data.specialization);
}
```

### 3. Authentication Check
```javascript
// Check if user is authenticated and get their data
async function checkAuthAndGetUserData() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        redirectToLogin();
        return null;
    }
    
    try {
        const response = await fetch('/credential/user-data', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            return userData;
        } else {
            // Token expired or invalid
            localStorage.removeItem('token');
            redirectToLogin();
            return null;
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
        redirectToLogin();
        return null;
    }
}
```

## Error Handling

### 401 Unauthorized
- Missing or invalid JWT token
- Token expired

### 403 Forbidden
- User account is inactive
- Invalid user role

### 404 Not Found
- User profile not found for the given role

## Use Cases

### 1. Dashboard Initialization
```javascript
// On app startup, get user data to initialize dashboard
const userData = await checkAuthAndGetUserData();
if (userData) {
    initializeDashboard(userData);
}
```

### 2. Profile Display
```javascript
// Display user profile information
function displayUserProfile(userData) {
    const profileSection = document.getElementById('profile-section');
    
    if (userData.role === 'patient') {
        profileSection.innerHTML = `
            <h2>Welcome, ${userData.profile_data.full_name}!</h2>
            <p>Age: ${userData.profile_data.age}</p>
            <p>Phone: ${userData.profile_data.phone_number}</p>
        `;
    }
}
```

### 3. Role-Based Navigation
```javascript
// Show different navigation based on user role
function setupNavigation(userData) {
    const nav = document.getElementById('navigation');
    
    switch(userData.role) {
        case 'patient':
            nav.innerHTML = `
                <a href="/patient/dashboard">Dashboard</a>
                <a href="/patient/appointments">Appointments</a>
                <a href="/patient/profile">Profile</a>
            `;
            break;
        case 'doctor':
            nav.innerHTML = `
                <a href="/doctor/dashboard">Dashboard</a>
                <a href="/doctor/patients">Patients</a>
                <a href="/doctor/schedule">Schedule</a>
            `;
            break;
        case 'ambulance':
            nav.innerHTML = `
                <a href="/ambulance/dashboard">Dashboard</a>
                <a href="/ambulance/emergencies">Emergencies</a>
                <a href="/ambulance/routes">Routes</a>
            `;
            break;
    }
}
```

## Benefits

1. **Single Source of Truth**: One endpoint for all user data
2. **Role-Specific Data**: Returns relevant profile information based on role
3. **Authentication Verification**: Validates JWT token and user status
4. **Frontend Flexibility**: Easy to implement user-specific interfaces
5. **Security**: Proper authentication and authorization checks 