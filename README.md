# Quantum-Safe Cryptography Platform

A comprehensive platform for testing and comparing classical and post-quantum cryptographic algorithms.

## 📁 Project Structure

```
Quantum-Cryptography-Project/
├── backend/          # Flask backend API (main application)
│   ├── instance/     # Database files
│   ├── routes/       # API endpoints
│   ├── app.py        # Main Flask application
│   ├── models.py     # Database models
│   └── ...          # Other backend files
├── .venv/           # Python virtual environment
└── README.md        # This file
```

## 🚀 Quick Start

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Start the server**:
   ```bash
   start_server.bat
   ```

3. **Access the API**:
   - Server: `http://localhost:5000`
   - Test frontend: `http://localhost:5000` (temporary)

## 📋 Phase 1 Implementation (Complete)

- ✅ Flask-based REST API with JWT authentication
- ✅ SQLite database with user management
- ✅ 13 cryptographic algorithms (6 classical + 7 post-quantum)
- ✅ Performance testing and analysis framework
- ✅ Comprehensive API documentation
- ✅ CORS-enabled for frontend integration

## 🔗 Documentation

- **[Backend Documentation](backend/README.md)** - Complete API documentation and setup guide
- **[Frontend Integration Guide](backend/FRONTEND_INTEGRATION.md)** - Guide for frontend developers

## 🔒 Algorithms Supported

### Classical Cryptography
- **RSA**: RSA-2048, RSA-4096
- **ECC**: ECC-P256, ECC-P384  
- **AES**: AES-128, AES-256

### Post-Quantum Cryptography
- **Kyber**: Kyber-512, Kyber-768, Kyber-1024
- **Dilithium**: Dilithium-2, Dilithium-3
- **Falcon**: Falcon-512, Falcon-1024

---

**Note**: This is Phase 1 of the project focusing on the backend API. Future phases will include a dedicated frontend application.
