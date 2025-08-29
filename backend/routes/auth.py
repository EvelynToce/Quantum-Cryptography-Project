from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, db
import re

auth_bp = Blueprint("auth", __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400

        username = data["username"].strip()
        email = data["email"].strip().lower()
        password = data["password"]

        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "access_token": access_token,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user"""
    try:
        data = request.get_json()
        print(f"DEBUG: Login attempt with data: {data}")

        # Validate required fields
        if not data.get("username") or not data.get("password"):
            print("DEBUG: Missing username or password")
            return jsonify({"error": "Username and password are required"}), 400

        username = data["username"].strip()
        password = data["password"]
        print(f"DEBUG: Attempting login for username: {username}")

        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            print(f"DEBUG: User not found: {username}")
            return jsonify({"error": "Invalid credentials"}), 401

        print(f"DEBUG: User found: {user.username}, checking password...")

        if not user.check_password(password):
            print("DEBUG: Password check failed")
            return jsonify({"error": "Invalid credentials"}), 401

        if not user.is_active:
            print("DEBUG: User account is deactivated")
            return jsonify({"error": "Account is deactivated"}), 401

        print("DEBUG: Login successful, creating token...")
        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "access_token": access_token,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"DEBUG: Login exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Login failed", "details": str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get profile", "details": str(e)}), 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        # Update username if provided
        if "username" in data:
            new_username = data["username"].strip()
            if new_username != user.username:
                if User.query.filter_by(username=new_username).first():
                    return jsonify({"error": "Username already exists"}), 400
                user.username = new_username

        # Update email if provided
        if "email" in data:
            new_email = data["email"].strip().lower()
            if new_email != user.email:
                if not validate_email(new_email):
                    return jsonify({"error": "Invalid email format"}), 400
                if User.query.filter_by(email=new_email).first():
                    return jsonify({"error": "Email already registered"}), 400
                user.email = new_email

        db.session.commit()

        return (
            jsonify(
                {"message": "Profile updated successfully", "user": user.to_dict()}
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ["current_password", "new_password"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400

        current_password = data["current_password"]
        new_password = data["new_password"]

        # Verify current password
        if not user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 400

        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Update password
        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to change password", "details": str(e)}), 500
