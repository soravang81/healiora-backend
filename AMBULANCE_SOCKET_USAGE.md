# Ambulance Request Socket Service Usage Guide

This guide explains how to use the enhanced ambulance request functionality in the socket service.

## Overview

The socket service now supports:
- Real-time ambulance requests from patients
- Automatic nearest hospital finding
- Location-based routing
- Hospital response handling
- Patient location tracking

## Socket Events

### 1. Connect to Socket

```javascript
// Connect with user ID and role
const socket = io('http://localhost:8000', {
  query: {
    userId: 'patient_123',
    role: 'patient'
  }
});
```

### 2. Update Patient Location

```javascript
// Update patient's current location
socket.emit('update_location', {
  patient_id: '123',
  latitude: 12.9716,
  longitude: 77.5946
});

// Listen for location update confirmation
socket.on('location_updated', (data) => {
  console.log('Location updated:', data.message);
});

socket.on('location_error', (data) => {
  console.error('Location error:', data.error);
});
```

### 3. Send Ambulance Request

```javascript
// Send ambulance request
socket.emit('ambulance_request', {
  patient_id: '123',
  latitude: 12.9716,  // Optional - will use stored location if not provided
  longitude: 77.5946, // Optional - will use stored location if not provided
  emergency_details: {
    symptoms: 'Chest pain, difficulty breathing',
    severity: 'high',
    notes: 'Patient is conscious but in pain'
  },
  timestamp: new Date().toISOString()
});

// Listen for request confirmation
socket.on('ambulance_request_confirmed', (data) => {
  console.log('Request confirmed:', data.message);
  console.log('Hospital:', data.hospital_name);
  console.log('Distance:', data.distance_km, 'km');
  console.log('Estimated time:', data.estimated_time);
});

// Listen for request errors
socket.on('ambulance_request_error', (data) => {
  console.error('Request error:', data.error);
});
```

### 4. Hospital Response (Hospital Side)

```javascript
// Hospital receives ambulance alert
socket.on('AMBULANCE_ALERT', (data) => {
  console.log('🚑 Ambulance request received:', data);
  
  // Data contains:
  // - patient_id, patient_name, patient_phone, patient_age, patient_gender
  // - emergency_contact, patient_latitude, patient_longitude
  // - hospital_id, hospital_name, distance_km
  // - emergency_details, request_timestamp
  
  // Accept the request
  socket.emit('hospital_response', {
    patient_id: data.patient_id,
    hospital_id: data.hospital_id,
    response: 'accepted',
    details: {
      ambulance_id: 'AMB001',
      estimated_arrival: '15 minutes',
      driver_phone: '+1234567890'
    }
  });
  
  // Or reject the request
  socket.emit('hospital_response', {
    patient_id: data.patient_id,
    hospital_id: data.hospital_id,
    response: 'rejected',
    details: {
      reason: 'No ambulances available',
      alternative_hospital: 'City General Hospital'
    }
  });
});
```

### 5. Patient Receives Response

```javascript
// Patient listens for hospital response
socket.on('ambulance_accepted', (data) => {
  console.log('✅ Ambulance accepted:', data.message);
  console.log('Details:', data.details);
});

socket.on('ambulance_rejected', (data) => {
  console.log('❌ Ambulance rejected:', data.message);
  console.log('Details:', data.details);
});
```

## Complete Example

### Patient Side (Frontend)

```javascript
import io from 'socket.io-client';

class AmbulanceService {
  constructor(patientId) {
    this.patientId = patientId;
    this.socket = io('http://localhost:8000', {
      query: {
        userId: patientId,
        role: 'patient'
      }
    });
    
    this.setupListeners();
  }
  
  setupListeners() {
    this.socket.on('connect', () => {
      console.log('Connected to ambulance service');
    });
    
    this.socket.on('ambulance_request_confirmed', (data) => {
      this.showNotification('Request sent successfully', 'success');
    });
    
    this.socket.on('ambulance_accepted', (data) => {
      this.showNotification('Ambulance is on the way!', 'success');
    });
    
    this.socket.on('ambulance_rejected', (data) => {
      this.showNotification('Request could not be fulfilled', 'error');
    });
  }
  
  updateLocation(latitude, longitude) {
    this.socket.emit('update_location', {
      patient_id: this.patientId,
      latitude,
      longitude
    });
  }
  
  requestAmbulance(emergencyDetails) {
    // Get current location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          
          this.socket.emit('ambulance_request', {
            patient_id: this.patientId,
            latitude,
            longitude,
            emergency_details: emergencyDetails,
            timestamp: new Date().toISOString()
          });
        },
        (error) => {
          // Use stored location or default
          this.socket.emit('ambulance_request', {
            patient_id: this.patientId,
            emergency_details: emergencyDetails,
            timestamp: new Date().toISOString()
          });
        }
      );
    }
  }
  
  showNotification(message, type) {
    // Implement your notification system
    console.log(`${type.toUpperCase()}: ${message}`);
  }
}

// Usage
const ambulanceService = new AmbulanceService('patient_123');

// Update location when app starts
ambulanceService.updateLocation(12.9716, 77.5946);

// Request ambulance
ambulanceService.requestAmbulance({
  symptoms: 'Chest pain, shortness of breath',
  severity: 'high',
  notes: 'Patient is conscious but in severe pain'
});
```

### Hospital Side (Frontend)

```javascript
import io from 'socket.io-client';

class HospitalAmbulanceService {
  constructor(hospitalId) {
    this.hospitalId = hospitalId;
    this.socket = io('http://localhost:8000', {
      query: {
        userId: hospitalId,
        role: 'hospital'
      }
    });
    
    this.setupListeners();
  }
  
  setupListeners() {
    this.socket.on('connect', () => {
      console.log('Hospital connected to ambulance service');
    });
    
    this.socket.on('AMBULANCE_ALERT', (data) => {
      this.handleAmbulanceRequest(data);
    });
  }
  
  handleAmbulanceRequest(data) {
    // Show notification to hospital staff
    this.showAmbulanceAlert(data);
    
    // You can implement automatic acceptance or manual review
    // For now, we'll show a manual review interface
  }
  
  acceptAmbulanceRequest(patientId, details) {
    this.socket.emit('hospital_response', {
      patient_id: patientId,
      hospital_id: this.hospitalId,
      response: 'accepted',
      details: details
    });
  }
  
  rejectAmbulanceRequest(patientId, reason) {
    this.socket.emit('hospital_response', {
      patient_id: patientId,
      hospital_id: this.hospitalId,
      response: 'rejected',
      details: { reason }
    });
  }
  
  showAmbulanceAlert(data) {
    // Implement your notification system
    console.log('🚑 AMBULANCE REQUEST:', data);
    
    // Example: Show a modal or notification
    const message = `
      Patient: ${data.patient_name}
      Age: ${data.patient_age}
      Phone: ${data.patient_phone}
      Distance: ${data.distance_km} km
      Symptoms: ${data.emergency_details.symptoms}
    `;
    
    alert(message);
  }
}

// Usage
const hospitalService = new HospitalAmbulanceService('hospital_456');
```

## Database Requirements

Make sure your hospitals have latitude and longitude coordinates set:

```sql
-- Update hospital with coordinates
UPDATE hospitals 
SET latitude = 12.9716, longitude = 77.5946 
WHERE id = 1;
```

## Error Handling

The service includes comprehensive error handling:

- Missing patient ID
- No hospitals available
- Hospital not connected
- Invalid coordinates
- Database errors

All errors are sent back to the client with descriptive messages.

## Security Considerations

1. **Authentication**: Ensure proper authentication before allowing socket connections
2. **Authorization**: Verify user roles and permissions
3. **Rate Limiting**: Implement rate limiting for ambulance requests
4. **Data Validation**: Validate all incoming data
5. **Logging**: Log all ambulance requests for audit purposes

## Testing

You can test the service using a simple test script:

```javascript
// Test script
const io = require('socket.io-client');

// Connect as patient
const patientSocket = io('http://localhost:8000', {
  query: { userId: 'test_patient', role: 'patient' }
});

// Connect as hospital
const hospitalSocket = io('http://localhost:8000', {
  query: { userId: 'test_hospital', role: 'hospital' }
});

// Test ambulance request
patientSocket.emit('ambulance_request', {
  patient_id: 'test_patient',
  latitude: 12.9716,
  longitude: 77.5946,
  emergency_details: { symptoms: 'Test emergency' }
});
```

This enhanced socket service provides a complete ambulance request system with real-time communication between patients and hospitals. 