# Quantum-Safe Cryptography Platform - Backend

A Flask-based backend API for testing and comparing classical and post-quantum cryptographic algorithms.

## 🚀 Features

### Phase 1 Implementation (Complete)
- **User Authentication**: Register, login, logout with JWT tokens
- **Algorithm Management**: Support for classical (RSA, ECC, AES) and post-quantum (Kyber, Dilithium, Falcon) algorithms
- **Testing Framework**: Run encryption, decryption, signing, and verification tests
- **Performance Analysis**: Track execution times and success rates
- **Reporting System**: Generate performance, security, and comparison reports
- **SQLite Database**: Store users, algorithms, tests, and reports

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### Algorithms
- `GET /api/algorithms/` - Get all algorithms
- `GET /api/algorithms/<id>` - Get specific algorithm
- `GET /api/algorithms/categories` - Get algorithm categories
- `POST /api/algorithms/<id>/test` - Test algorithm
- `GET /api/algorithms/<id>/tests` - Get algorithm test history
- `POST /api/algorithms/compare` - Compare multiple algorithms
- `POST /api/algorithms/seed` - Seed database with algorithms

### Tests
- `GET /api/tests/` - Get user's tests (with pagination)
- `GET /api/tests/<id>` - Get specific test
- `DELETE /api/tests/<id>` - Delete test
- `GET /api/tests/statistics` - Get test statistics
- `POST /api/tests/bulk-delete` - Delete multiple tests
- `GET /api/tests/export` - Export tests to JSON
- `GET /api/tests/performance-trends` - Get performance trends

### Reports
- `GET /api/reports/` - Get user's reports
- `GET /api/reports/<id>` - Get specific report
- `DELETE /api/reports/<id>` - Delete report
- `POST /api/reports/generate/performance` - Generate performance report
- `POST /api/reports/generate/security` - Generate security report
- `POST /api/reports/generate/comparison` - Generate comparison report
- `GET /api/reports/types` - Get available report types

### Health Check
- `GET /api/health` - API health check

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Quick Start

1. **Clone and navigate to the project**:
   ```bash
   cd Quantum-Cryptography-Project/backend
   ```

2. **Activate virtual environment** (already configured):
   ```bash
   # Windows
   ..\.venv\Scripts\activate
   
   # Linux/Mac
   source ../.venv/bin/activate
   ```

3. **Install dependencies** (already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

5. **Start the server**:
   ```bash
   python app.py
   ```
   
   Or use the batch file:
   ```bash
   start_server.bat
   ```

6. **Test the backend**:
   ```bash
   python test_backend.py
   ```

The server will start at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and customize:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DEBUG=True
```

### Database
- SQLite database file: `quantum_crypto.db`
- Automatically created when running `init_db.py`

## 📊 Supported Algorithms

### Classical Cryptography
- **RSA**: 2048-bit, 4096-bit
- **ECC**: P-256, P-384 curves
- **AES**: 128-bit, 256-bit

### Post-Quantum Cryptography
- **Kyber** (KEM): 512, 768, 1024 security levels
- **Dilithium** (Signatures): Level 2, 3, 5
- **Falcon** (Signatures): 512, 1024-bit

## 🧪 Testing

### Test Types Supported
- **Encryption/Decryption**: Test symmetric and asymmetric encryption
- **Key Generation**: Measure key generation performance
- **Digital Signatures**: Sign and verify messages (for signature algorithms)

### Performance Metrics
- Execution time (milliseconds)
- Success/failure rates
- Key sizes and security levels
- Quantum safety assessment

## 📈 Reports

### Report Types
1. **Performance Reports**: Analyze execution times and efficiency
2. **Security Reports**: Assess quantum readiness and security levels
3. **Comparison Reports**: Compare multiple algorithms side-by-side

### Features
- Exportable data (JSON format)
- Historical trend analysis
- Recommendations based on results
- Customizable time periods

## 🔐 Security Features

- **Password hashing** with bcrypt
- **JWT token authentication**
- **Input validation** and sanitization
- **CORS protection**
- **SQL injection prevention** with SQLAlchemy ORM

## 📝 Database Schema

### Tables
- **Users**: User accounts and authentication
- **Algorithms**: Available cryptographic algorithms
- **Tests**: Algorithm test results and performance data
- **Reports**: Generated analysis reports

## 🤝 Frontend Integration

### For Your Partner
The backend provides a complete REST API that can be consumed by any frontend framework:

1. **Authentication**: Use JWT tokens for API access
2. **CORS**: Configured to allow frontend connections
3. **JSON Format**: All data exchanged in JSON format
4. **Error Handling**: Consistent error responses
5. **Documentation**: Each endpoint documented above

### Example API Usage
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});

// Use token for authenticated requests
const token = loginResponse.json().access_token;
const algorithmsResponse = await fetch('http://localhost:5000/api/algorithms/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## 📁 Project Structure

```
Quantum-Cryptography-Project/
├── app.py                    # Flask application entry point
├── models.py                 # Database models
├── crypto_implementations.py # Cryptographic algorithm implementations
├── init_db.py               # Database initialization script
├── test_backend.py          # Backend testing script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .env.example            # Environment template
├── start_server.bat        # Windows startup script
├── routes/                 # API route modules
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── algorithms.py      # Algorithm routes
│   ├── tests.py           # Test management routes
│   └── reports.py         # Report generation routes
└── README.md              # This file
```

## 🚨 Known Limitations

1. **Post-Quantum Implementations**: Current PQC implementations are simplified/mock versions for demonstration. Production use would require proper libraries like `liboqs`.

2. **Performance**: Cryptographic operations are synchronous. For production, consider async processing for heavy operations.

3. **Security**: Current setup uses development configurations. Production deployment requires proper secret management.

## 🔮 Future Enhancements (Beyond Phase 1)

- Integration with proper PQC libraries
- WebSocket support for real-time updates
- Advanced analytics and machine learning
- Multi-user collaboration features
- Container deployment (Docker)
- Cloud deployment options

## 🆘 Troubleshooting

### Common Issues

1. **Module Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Run `python init_db.py` to initialize
3. **Port Conflicts**: Flask runs on port 5000 by default
4. **CORS Issues**: Check CORS configuration in `app.py`

### Testing the Backend
Run `python test_backend.py` to verify all endpoints are working correctly.

## 📞 Support

If you encounter any issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Verify the database is properly initialized
4. Check that no other service is using port 5000

The backend is now ready for frontend integration! 🎉
