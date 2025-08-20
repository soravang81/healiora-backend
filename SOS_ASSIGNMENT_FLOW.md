# SOS Assignment Flow Documentation

## Overview

This document explains the complete flow for handling SOS requests with doctor and ambulance assignment after hospital acceptance.

## Complete Flow

1. **Patient sends SOS request** → Hospital receives notification
2. **Hospital accepts request** → Show doctor selection
3. **Select doctor** → Show ambulance selection  
4. **Select ambulance** → Send complete assignment
5. **Backend processes** → Notifies patient, doctor, and ambulance driver

## Socket Events

### 1. Get Available Doctors

**Event:** `get_available_doctors`

**Request:**
```javascript
socket.emit('get_available_doctors', {
  hospital_id: 1
});
```

**Response:**
```javascript
socket.on('available_doctors', (data) => {
  console.log('Available doctors:', data.doctors);
  // data.doctors contains array of:
  // {
  //   id: 1,
  //   name: "Dr. John Doe",
  //   specialization: "Cardiology",
  //   phone: "+1234567890",
  //   email: "john@hospital.com",
  //   is_available: true
  // }
});

socket.on('available_doctors_error', (data) => {
  console.error('Error:', data.error);
});
```

### 2. Get Available Ambulances

**Event:** `get_available_ambulances`

**Request:**
```javascript
socket.emit('get_available_ambulances', {
  hospital_id: 1
});
```

**Response:**
```javascript
socket.on('available_ambulances', (data) => {
  console.log('Available ambulances:', data.ambulances);
  // data.ambulances contains array of:
  // {
  //   id: 1,
  //   vehicle_number: "AMB-001",
  //   driver_name: "Mike Johnson",
  //   driver_phone: "+1234567890",
  //   is_available: true,
  //   current_location: {
  //     latitude: 12.9716,
  //     longitude: 77.5946
  //   }
  // }
});

socket.on('available_ambulances_error', (data) => {
  console.error('Error:', data.error);
});
```

### 3. Assign Doctor and Ambulance

**Event:** `assign_doctor_and_ambulance`

**Request:**
```javascript
socket.emit('assign_doctor_and_ambulance', {
  patient_id: "123",
  hospital_id: 1,
  doctor_id: 5,
  ambulance_id: 10,
  case_details: {
    symptoms: "Chest pain, difficulty breathing",
    severity: "high",
    estimated_arrival: "15 minutes",
    notes: "Patient is conscious but in pain"
  }
});
```

**Response:**
```javascript
socket.on('assignment_success', (data) => {
  console.log('Assignment successful:', data.message);
  // data contains:
  // {
  //   message: "Doctor and ambulance assigned successfully",
  //   patient_id: "123",
  //   doctor_id: 5,
  //   ambulance_id: 10
  // }
});

socket.on('assignment_error', (data) => {
  console.error('Assignment error:', data.error);
});
```

### 4. Patient Receives Assignment Notification

**Event:** `doctor_ambulance_assigned`

**Patient receives:**
```javascript
socket.on('doctor_ambulance_assigned', (data) => {
  console.log('Doctor and ambulance assigned:', data);
  // data contains:
  // {
  //   message: "Doctor and ambulance have been assigned to your case!",
  //   doctor: {
  //     id: 5,
  //     name: "Dr. John Doe",
  //     specialization: "Cardiology",
  //     phone: "+1234567890"
  //   },
  //   ambulance: {
  //     id: 10,
  //     vehicle_number: "AMB-001",
  //     driver_name: "Mike Johnson",
  //     driver_phone: "+1234567890"
  //   },
  //   estimated_arrival: "15 minutes",
  //   case_details: {...}
  // }
});
```

## Flutter Implementation Example

```dart
import 'package:socket_io_client/socket_io_client.dart' as IO;

class SOSService {
  late IO.Socket socket;
  
  void connectToSocket() {
    socket = IO.io('http://your-backend:8000', <String, dynamic>{
      'transports': ['websocket'],
      'query': {
        'role': 'hospital', // or 'patient'
        'token': 'your-jwt-token'
      }
    });
    
    // Listen for SOS requests (Hospital side)
    socket.on('sos_request', (data) {
      // Show SOS request with patient details
      // Display confirm button
    });
    
    // Listen for assignment confirmation (Patient side)
    socket.on('doctor_ambulance_assigned', (data) {
      // Show doctor and ambulance details to patient
      // Display contact information
    });
  }
  
  void getAvailableDoctors(int hospitalId) {
    socket.emit('get_available_doctors', {'hospital_id': hospitalId});
    socket.on('available_doctors', (data) {
      // Update UI with available doctors
      // Show doctor selection dropdown
    });
  }
  
  void getAvailableAmbulances(int hospitalId) {
    socket.emit('get_available_ambulances', {'hospital_id': hospitalId});
    socket.on('available_ambulances', (data) {
      // Update UI with available ambulances
      // Show ambulance selection dropdown
    });
  }
  
  void assignDoctorAndAmbulance({
    required String patientId,
    required int hospitalId,
    required int doctorId,
    required int ambulanceId,
    required Map<String, dynamic> caseDetails,
  }) {
    socket.emit('assign_doctor_and_ambulance', {
      'patient_id': patientId,
      'hospital_id': hospitalId,
      'doctor_id': doctorId,
      'ambulance_id': ambulanceId,
      'case_details': caseDetails,
    });
    
    socket.on('assignment_success', (data) {
      // Show success message
      // Update UI to show assignment complete
    });
  }
}
```

## Database Logging

All assignment events are logged in the `socket_logs` table with:
- Event type: `doctor_ambulance_assignment`
- User role: `hospital`
- Status: `pending` → `success` or `failed`
- Response data containing assignment details

## Error Handling

- Missing required fields
- Doctor or ambulance not found
- Patient not connected
- Database errors

All errors are logged and sent back to the client with appropriate error messages.
