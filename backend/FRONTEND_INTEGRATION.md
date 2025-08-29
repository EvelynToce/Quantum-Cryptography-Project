# Quantum-Safe Cryptography Platform - Frontend Integration Guide

Hi! This document will help you integrate with the Flask backend that's now ready for Phase 1.

## 🚀 Backend Status: READY ✅

The backend is complete and fully functional with all Phase 1 requirements implemented:

- ✅ User authentication (register/login/logout)
- ✅ Algorithm management (13 algorithms: 6 classical + 7 post-quantum)
- ✅ Testing framework (encryption, decryption, key generation)
- ✅ Performance tracking and statistics
- ✅ Report generation (performance, security, comparison)
- ✅ SQLite database with all required tables

## 🌐 API Base URL

```
http://localhost:5000/api
```

## 🔑 Authentication Flow

### 1. Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "your_username",
  "email": "user@example.com", 
  "password": "SecurePassword123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "created_at": "2025-08-29T02:40:00",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "SecurePassword123"
}
```

### 3. Use Token for Protected Endpoints
```http
Authorization: Bearer your_jwt_token_here
```

## 📊 Available Algorithms

The backend comes pre-seeded with these algorithms:

### Classical Algorithms (🟡)
- RSA-2048, RSA-4096
- ECC-P256, ECC-P384  
- AES-128, AES-256

### Post-Quantum Algorithms (🟢)
- Kyber-512, Kyber-768, Kyber-1024
- Dilithium-2, Dilithium-3
- Falcon-512, Falcon-1024

## 🧪 Testing Algorithms

### Get All Algorithms
```http
GET /api/algorithms/
Authorization: Bearer your_token
```

### Test an Algorithm
```http
POST /api/algorithms/{algorithm_id}/test
Authorization: Bearer your_token
Content-Type: application/json

{
  "test_type": "encryption",
  "input_data": "Hello, Quantum World!"
}
```

**Response:**
```json
{
  "message": "Test completed successfully",
  "test": {
    "id": 1,
    "algorithm_id": 1,
    "test_type": "encryption",
    "execution_time": 45.67,
    "success": true,
    "created_at": "2025-08-29T02:40:00"
  },
  "result": "base64_encoded_result..."
}
```

## 📈 Statistics & Reports

### Get Test Statistics
```http
GET /api/tests/statistics
Authorization: Bearer your_token
```

### Generate Performance Report
```http
POST /api/reports/generate/performance
Authorization: Bearer your_token
Content-Type: application/json

{
  "algorithm_ids": [1, 2, 3],
  "title": "My Performance Report",
  "days": 30
}
```

## 🎨 Frontend Integration Tips

### 1. Authentication State Management
Store the JWT token and include it in all requests:

```javascript
// Store token
localStorage.setItem('token', response.access_token);

// Use in requests
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
};
```

### 2. Algorithm Categories
Display algorithms by type:
- Classical algorithms: Show with warning about quantum vulnerability
- Post-quantum algorithms: Show as "future-safe"

### 3. Performance Visualization
- Execution times (bar charts)
- Success rates (pie charts)  
- Performance trends over time (line graphs)

### 4. Error Handling
All errors return JSON with `error` field:
```json
{
  "error": "Algorithm not found",
  "details": "Additional error information"
}
```

## 🚀 Quick Start for Frontend

1. **Start the backend:**
   ```bash
   cd Quantum-Cryptography-Project
   python app.py
   ```

2. **Test connection:**
   ```javascript
   fetch('http://localhost:5000/api/health')
     .then(response => response.json())
     .then(data => console.log(data));
   ```

3. **Create your first user and get algorithms:**
   ```javascript
   // Register
   const registerResponse = await fetch('http://localhost:5000/api/auth/register', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       username: 'testuser',
       email: 'test@example.com', 
       password: 'SecurePassword123'
     })
   });
   
   const { access_token } = await registerResponse.json();
   
   // Get algorithms
   const algorithmsResponse = await fetch('http://localhost:5000/api/algorithms/', {
     headers: { 'Authorization': `Bearer ${access_token}` }
   });
   
   const { algorithms } = await algorithmsResponse.json();
   console.log('Available algorithms:', algorithms);
   ```

## 📁 Project Structure for You

```
frontend/                     # Your frontend project
├── src/
│   ├── components/
│   │   ├── Auth/            # Login/Register components
│   │   ├── Algorithms/      # Algorithm list/testing
│   │   ├── Dashboard/       # Statistics dashboard
│   │   └── Reports/         # Report generation/viewing
│   ├── services/
│   │   └── api.js          # API communication functions
│   └── utils/
│       └── auth.js         # Token management
└── backend/                 # Already completed!
    ├── app.py              # Flask server
    ├── models.py           # Database models
    └── routes/             # API endpoints
```

## 🛠️ Suggested Tech Stack

Since you're handling the frontend, here are some recommendations:

- **React/Vue/Angular**: For the main framework
- **Chart.js/D3.js**: For performance visualizations
- **Axios/Fetch**: For API calls
- **React Router/Vue Router**: For navigation
- **Bootstrap/Tailwind**: For styling

## ⚡ Development Workflow

1. **Start backend:** `python app.py` (runs on port 5000)
2. **Start frontend:** Your choice (typically port 3000)
3. **CORS is configured** to allow frontend connections
4. **Test endpoints** using the provided examples

## 🔍 Debugging

- Backend logs appear in the Python console
- API returns detailed error messages
- Use browser dev tools to inspect API calls
- Test individual endpoints with Postman/curl

## 📞 Need Help?

If you run into any issues:

1. **Check the backend is running:** Visit http://localhost:5000/api/health
2. **Verify your requests:** Check headers and JSON format
3. **Look at backend logs:** Error details appear in the Python console
4. **Test with demo script:** Run `python demo_backend.py` to verify backend

## 🎯 Phase 1 Features to Implement in Frontend

### Must-Have (Core Features)
- [ ] User registration/login page
- [ ] Algorithm selection interface  
- [ ] Test algorithm functionality
- [ ] Basic results display
- [ ] Simple performance metrics

### Nice-to-Have (Enhanced UX)
- [ ] Dashboard with statistics
- [ ] Performance charts and graphs
- [ ] Report generation interface
- [ ] Algorithm comparison tools
- [ ] Export functionality

---

**The backend is ready and waiting for your frontend! 🚀**

All the heavy lifting (crypto algorithms, database, authentication, API) is done. You can focus entirely on creating a great user interface and experience.

Good luck with the frontend development! The backend will handle all the complex cryptographic operations seamlessly.
