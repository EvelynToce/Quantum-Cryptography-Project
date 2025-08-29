from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Global variables for db and bcrypt - will be initialized by app
db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    """User model for authentication"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    tests = db.relationship("Test", backref="user", lazy=True)
    reports = db.relationship("Report", backref="user", lazy=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class Algorithm(db.Model):
    """Algorithm model for storing cryptographic algorithms"""

    __tablename__ = "algorithms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'classical' or 'post-quantum'
    category = db.Column(
        db.String(50), nullable=False
    )  # 'RSA', 'ECC', 'AES', 'Kyber', 'Dilithium', 'Falcon'
    key_size = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    quantum_safe = db.Column(db.Boolean, default=False)
    implementation_status = db.Column(
        db.String(20), default="active"
    )  # 'active', 'deprecated', 'experimental'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tests = db.relationship("Test", backref="algorithm", lazy=True)

    def to_dict(self):
        """Convert algorithm to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "key_size": self.key_size,
            "description": self.description,
            "quantum_safe": self.quantum_safe,
            "implementation_status": self.implementation_status,
            "created_at": self.created_at.isoformat(),
        }


class Test(db.Model):
    """Test model for storing algorithm test results"""

    __tablename__ = "tests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithms.id"), nullable=False)
    test_type = db.Column(
        db.String(50), nullable=False
    )  # 'encryption', 'decryption', 'signing', 'verification'
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # in milliseconds
    success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text)
    test_metadata = db.Column(db.JSON)  # Additional test parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert test to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "algorithm_id": self.algorithm_id,
            "test_type": self.test_type,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "execution_time": self.execution_time,
            "success": self.success,
            "error_message": self.error_message,
            "test_metadata": self.test_metadata,
            "created_at": self.created_at.isoformat(),
        }


class Report(db.Model):
    """Report model for storing analysis reports"""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(
        db.String(50), nullable=False
    )  # 'performance', 'security', 'comparison'
    content = db.Column(db.JSON)  # Report data in JSON format
    algorithms_tested = db.Column(db.JSON)  # List of algorithm IDs included in report
    summary = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert report to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "report_type": self.report_type,
            "content": self.content,
            "algorithms_tested": self.algorithms_tested,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }
