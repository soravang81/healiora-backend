# Healiora Backend API

A comprehensive healthcare management system backend built with FastAPI, PostgreSQL, and Socket.IO for real-time communication.

## 🏥 Project Overview

Healiora is a healthcare management platform that connects patients, hospitals, doctors, and ambulance services. The system provides APIs for user authentication, patient management, hospital operations, doctor management, ambulance services, and medical records.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Redis (for Socket.IO)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd healiora-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/healiora
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   debug=False
   db_user=your_db_user
   db_password=your_db_password
   db_host=localhost
   db_port=5432
   db_name=healiora
   ```

5. **Database Setup**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-access-token>
```

## 🔐 Authentication APIs

### User Registration
```http
POST /api/v1/users/register
Content-Type: application/json

{
  "email": "patient@example.com",
  "password": "password123",
  "phone_number": "+1234567890",
  "role": "patient",
  "username": "john_doe",
  "age": 30,
  "emergency_contact": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "patient@example.com",
  "phone_number": "+1234567890",
  "role": "patient",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

### User Login
```http
POST /api/v1/users/login
Content-Type: application/json

{
  "email": "patient@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Admin Login
```http
POST /api/v1/users/login-admin
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### Get User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

## 👥 Patient APIs

### Create Patient Profile
```http
POST /api/v1/patients/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "john_doe",
  "age": 30,
  "emergency_contact": "+1234567890"
}
```

### Get Patient Profile
```http
GET /api/v1/patients/me
Authorization: Bearer <token>
```

### Get Patient by ID (Admin Only)
```http
GET /api/v1/patients/{patient_id}
Authorization: Bearer <admin-token>
```

## 🏥 Hospital APIs

### Create Hospital (Admin Only)
```http
POST /api/v1/hospitals/create
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "email": "hospital@example.com",
  "password": "hospital123",
  "name": "City General Hospital",
  "address": "123 Main Street, City",
  "phone": "+1234567890",
  "admin_name": "Dr. Smith",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### Hospital Login
```http
POST /api/v1/hospitals/login
Content-Type: application/json

{
  "email": "hospital@example.com",
  "password": "hospital123"
}
```

### Get Hospital Profile
```http
GET /api/v1/hospitals/me
Authorization: Bearer <hospital-token>
```

### Get All Hospitals
```http
GET /api/v1/hospitals/all
```

### Get Hospital by ID
```http
GET /api/v1/hospitals/{hospital_id}
```

### Update Hospital (Admin Only)
```http
PUT /api/v1/hospitals/{hospital_id}
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "name": "Updated Hospital Name",
  "address": "New Address",
  "phone": "+1234567890"
}
```

## 👨‍⚕️ Doctor APIs

### Create Doctor (Hospital Only)
```http
POST /api/v1/doctors/
Authorization: Bearer <hospital-token>
Content-Type: application/json

{
  "name": "Dr. John Smith",
  "phone_number": "+1234567890",
  "email": "doctor@example.com",
  "address": "123 Medical Center Dr",
  "education": "MD, Cardiology",
  "specialization": "Cardiology",
  "years_of_experience": 10.5
}
```

### Doctor Login
```http
POST /api/v1/doctors/login-doctor
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "doctor123"
}
```

### Get All Doctors
```http
GET /api/v1/doctors/
```

### Get Doctor by ID
```http
GET /api/v1/doctors/{doctor_id}
```

### Get Doctors by Hospital
```http
GET /api/v1/doctors/hospital/{hospital_id}
```

## 🚑 Ambulance APIs

### Create Ambulance (Hospital Only)
```http
POST /api/v1/ambulances/
Authorization: Bearer <hospital-token>
Content-Type: application/json

{
  "ambulance_number": "AMB001",
  "driver_name": "John Driver",
  "driver_phone": "+1234567890",
  "driver_email": "driver@example.com",
  "vehicle_type": "Emergency Ambulance"
}
```

### Ambulance Login
```http
POST /api/v1/ambulances/login
Content-Type: application/json

{
  "email": "driver@example.com",
  "password": "driver123"
}
```

### Get All Ambulances
```http
GET /api/v1/ambulances/
```

### Get Ambulance by ID
```http
GET /api/v1/ambulances/{ambulance_id}
```

### Get Ambulances by Hospital
```http
GET /api/v1/ambulances/hospital/{hospital_id}
```

## 📋 Medical Records APIs

### Create Medical Record
```http
POST /api/v1/medical-records/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "date_of_birth": "1990-01-01",
  "blood_group": "O+",
  "past_surgeries": "Appendectomy in 2015",
  "long_term_medications": "None",
  "ongoing_illnesses": "None",
  "allergies": "Penicillin",
  "other_issues": "None",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_number": "+1234567890"
}
```

### Get Medical Record
```http
GET /api/v1/medical-records/me
Authorization: Bearer <token>
```

### Update Medical Record
```http
PUT /api/v1/medical-records/update
Authorization: Bearer <token>
Content-Type: application/json

{
  "blood_group": "A+",
  "allergies": "Penicillin, Sulfa drugs"
}
```

### Delete Medical Record
```http
DELETE /api/v1/medical-records/delete
Authorization: Bearer <token>
```

## 🔌 Socket.IO Integration

The backend includes Socket.IO for real-time communication:

**Connection:**
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000/socket.io/');

socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

## 📊 Data Models & Schemas

### User Roles
- `patient`: Regular patient users
- `hospital`: Hospital administrators
- `doctor`: Medical professionals
- `admin`: System administrators

### Database Models
- **Credential**: User authentication and roles
- **Patient**: Patient profiles and information
- **Hospital**: Hospital details and locations
- **Doctor**: Medical professional information
- **Ambulance**: Emergency vehicle and driver details
- **MedicalRecord**: Patient medical history

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS middleware for frontend integration
- Input validation with Pydantic schemas

## 🛠️ Development

### Running in Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### API Documentation
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## 🚀 Production Deployment

1. **Environment Variables**
   - Set `DATABASE_URL` to production PostgreSQL
   - Use strong `SECRET_KEY`
   - Set `debug=False`

2. **Database**
   - Use production PostgreSQL instance
   - Run migrations: `alembic upgrade head`

3. **Server**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

## 📱 Frontend Integration Examples

### React/JavaScript Example
```javascript
// Authentication
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/v1/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  return response.json();
};

// Protected API call
const getPatientProfile = async (token) => {
  const response = await fetch('http://localhost:8000/api/v1/patients/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
};
```

### Error Handling
```javascript
const handleApiError = (error) => {
  if (error.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (error.status === 403) {
    // Show access denied message
    alert('Access denied');
  } else {
    // Show generic error
    alert('An error occurred');
  }
};
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

---

**Note**: This is a development setup. For production deployment, ensure proper security measures, environment variables, and database configurations are in place. 