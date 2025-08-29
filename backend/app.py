from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "quantum-crypto-secret-key-change-in-production"
)
# Use absolute path for database
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "quantum_crypto.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "jwt-secret-string-change-in-production"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Initialize models with app
from models import db, bcrypt

db.init_app(app)
bcrypt.init_app(app)

# Initialize other extensions
jwt = JWTManager(app)
CORS(app)


# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"DEBUG: Token expired - header: {jwt_header}, payload: {jwt_payload}")
    return (
        jsonify({"error": "Token has expired", "message": "The JWT token has expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"DEBUG: Invalid token - error: {error}")
    return (
        jsonify({"error": "Invalid token", "message": "The JWT token is invalid"}),
        422,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"DEBUG: Missing token - error: {error}")
    return (
        jsonify(
            {"error": "Authorization token required", "message": "No JWT token found"}
        ),
        401,
    )


# Import models and routes after initialization
from models import User, Algorithm, Test, Report
from routes.auth import auth_bp
from routes.algorithms import algorithms_bp
from routes.tests import tests_bp
from routes.reports import reports_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(algorithms_bp, url_prefix="/api/algorithms")
app.register_blueprint(tests_bp, url_prefix="/api/tests")
app.register_blueprint(reports_bp, url_prefix="/api/reports")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "message": "Quantum-Safe Cryptography Platform API is running",
        }
    )


@app.route("/")
def index():
    """Serve the test frontend"""
    return send_from_directory(".", "frontend_test.html")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Current working directory: {os.getcwd()}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
