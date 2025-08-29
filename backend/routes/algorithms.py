from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Algorithm, Test, db
from crypto_implementations import (
    RSACrypto,
    ECCCrypto,
    AESCrypto,
    KyberCrypto,
    DilithiumCrypto,
    FalconCrypto,
)
import time
import traceback

algorithms_bp = Blueprint("algorithms", __name__)

# Algorithm implementations mapping
ALGORITHM_IMPLEMENTATIONS = {
    "RSA": RSACrypto,
    "ECC": ECCCrypto,
    "AES": AESCrypto,
    "Kyber": KyberCrypto,
    "Dilithium": DilithiumCrypto,
    "Falcon": FalconCrypto,
}


@algorithms_bp.route("/", methods=["GET"])
def get_algorithms():
    """Get all available algorithms"""
    try:
        algorithms = Algorithm.query.all()
        return jsonify({"algorithms": [algo.to_dict() for algo in algorithms]}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch algorithms", "details": str(e)}), 500


@algorithms_bp.route("/<int:algorithm_id>", methods=["GET"])
def get_algorithm(algorithm_id):
    """Get specific algorithm details"""
    try:
        algorithm = Algorithm.query.get(algorithm_id)
        if not algorithm:
            return jsonify({"error": "Algorithm not found"}), 404

        return jsonify({"algorithm": algorithm.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch algorithm", "details": str(e)}), 500


@algorithms_bp.route("/categories", methods=["GET"])
def get_algorithm_categories():
    """Get algorithm categories with counts"""
    try:
        classical_count = Algorithm.query.filter_by(type="classical").count()
        post_quantum_count = Algorithm.query.filter_by(type="post-quantum").count()

        categories = (
            db.session.query(
                Algorithm.category, db.func.count(Algorithm.id).label("count")
            )
            .group_by(Algorithm.category)
            .all()
        )

        return (
            jsonify(
                {
                    "summary": {
                        "classical": classical_count,
                        "post_quantum": post_quantum_count,
                        "total": classical_count + post_quantum_count,
                    },
                    "categories": [
                        {"name": cat[0], "count": cat[1]} for cat in categories
                    ],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Failed to fetch categories", "details": str(e)}), 500


@algorithms_bp.route("/<int:algorithm_id>/test", methods=["POST"])
@jwt_required()
def test_algorithm(algorithm_id):
    """Test a specific algorithm"""
    try:
        current_user_id = int(get_jwt_identity())
        print(f"DEBUG: Testing algorithm {algorithm_id} for user {current_user_id}")

        algorithm = Algorithm.query.get(algorithm_id)

        if not algorithm:
            print(f"DEBUG: Algorithm {algorithm_id} not found")
            return jsonify({"error": "Algorithm not found"}), 404

        data = request.get_json() or {}
        test_type = data.get("test_type", "encryption")
        input_data = data.get("input_data", "Hello, Quantum World!")

        # Auto-correct test type for signature algorithms
        if algorithm.category in ["Dilithium", "Falcon"] and test_type == "encryption":
            test_type = "signing"
            print(
                f"DEBUG: Auto-corrected test type to 'signing' for {algorithm.category} algorithm"
            )

        print(
            f"DEBUG: Test type: {test_type}, Algorithm: {algorithm.name}, Category: {algorithm.category}"
        )

        # Get algorithm implementation
        implementation_class = ALGORITHM_IMPLEMENTATIONS.get(algorithm.category)
        if not implementation_class:
            error_msg = f"Implementation not available for {algorithm.category}"
            print(f"DEBUG: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Initialize algorithm implementation
        crypto_impl = implementation_class(key_size=algorithm.key_size)

        # Record start time
        start_time = time.time()

        try:
            # Perform the test based on type
            if test_type == "encryption":
                result = crypto_impl.encrypt(input_data)
                output_data = result
            elif test_type == "decryption":
                # For decryption test, first encrypt then decrypt
                encrypted = crypto_impl.encrypt(input_data)
                result = crypto_impl.decrypt(encrypted)
                output_data = result
            elif test_type == "key_generation":
                result = crypto_impl.generate_keys()
                output_data = {
                    "public_key_size": len(str(result.get("public_key", ""))),
                    "private_key_size": len(str(result.get("private_key", ""))),
                    "generated": True,
                }
            elif test_type == "signing" and hasattr(crypto_impl, "sign"):
                result = crypto_impl.sign(input_data)
                output_data = result
            elif test_type == "verification" and hasattr(crypto_impl, "verify"):
                # First sign, then verify
                signature = crypto_impl.sign(input_data)
                result = crypto_impl.verify(input_data, signature)
                output_data = {"verified": result}
            else:
                return jsonify({"error": f"Unsupported test type: {test_type}"}), 400

            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000  # in milliseconds

            # Create test record
            test_record = Test(
                user_id=current_user_id,
                algorithm_id=algorithm_id,
                test_type=test_type,
                input_data=input_data,
                output_data=str(output_data),
                execution_time=execution_time,
                success=True,
                test_metadata={
                    "key_size": algorithm.key_size,
                    "algorithm_type": algorithm.type,
                },
            )

            db.session.add(test_record)
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Test completed successfully",
                        "test": test_record.to_dict(),
                        "result": output_data,
                    }
                ),
                200,
            )

        except Exception as crypto_error:
            execution_time = (time.time() - start_time) * 1000

            # Create failed test record
            test_record = Test(
                user_id=current_user_id,
                algorithm_id=algorithm_id,
                test_type=test_type,
                input_data=input_data,
                output_data=None,
                execution_time=execution_time,
                success=False,
                error_message=str(crypto_error),
                test_metadata={
                    "key_size": algorithm.key_size,
                    "algorithm_type": algorithm.type,
                },
            )

            db.session.add(test_record)
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Test failed",
                        "test": test_record.to_dict(),
                        "error": str(crypto_error),
                    }
                ),
                400,
            )

    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Algorithm test error: {str(e)}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Failed to test algorithm", "details": str(e)}), 500


@algorithms_bp.route("/<int:algorithm_id>/tests", methods=["GET"])
@jwt_required()
def get_algorithm_tests(algorithm_id):
    """Get all tests for a specific algorithm"""
    try:
        current_user_id = get_jwt_identity()
        algorithm = Algorithm.query.get(algorithm_id)

        if not algorithm:
            return jsonify({"error": "Algorithm not found"}), 404

        # Get user's tests for this algorithm
        tests = (
            Test.query.filter_by(user_id=current_user_id, algorithm_id=algorithm_id)
            .order_by(Test.created_at.desc())
            .all()
        )

        return (
            jsonify(
                {
                    "algorithm": algorithm.to_dict(),
                    "tests": [test.to_dict() for test in tests],
                    "total_tests": len(tests),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Failed to fetch tests", "details": str(e)}), 500


@algorithms_bp.route("/compare", methods=["POST"])
@jwt_required()
def compare_algorithms():
    """Compare performance of multiple algorithms"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        algorithm_ids = data.get("algorithm_ids", [])
        test_data = data.get("test_data", "Hello, Quantum World!")

        if not algorithm_ids or len(algorithm_ids) < 2:
            return (
                jsonify({"error": "At least 2 algorithms required for comparison"}),
                400,
            )

        comparison_results = []

        for algo_id in algorithm_ids:
            algorithm = Algorithm.query.get(algo_id)
            if not algorithm:
                continue

            implementation_class = ALGORITHM_IMPLEMENTATIONS.get(algorithm.category)
            if not implementation_class:
                continue

            try:
                crypto_impl = implementation_class(key_size=algorithm.key_size)

                # Test encryption performance
                start_time = time.time()
                encrypted = crypto_impl.encrypt(test_data)
                encryption_time = (time.time() - start_time) * 1000

                # Test decryption performance
                start_time = time.time()
                decrypted = crypto_impl.decrypt(encrypted)
                decryption_time = (time.time() - start_time) * 1000

                # Test key generation performance
                start_time = time.time()
                keys = crypto_impl.generate_keys()
                key_gen_time = (time.time() - start_time) * 1000

                comparison_results.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "performance": {
                            "encryption_time_ms": encryption_time,
                            "decryption_time_ms": decryption_time,
                            "key_generation_time_ms": key_gen_time,
                            "total_time_ms": encryption_time
                            + decryption_time
                            + key_gen_time,
                        },
                        "success": decrypted == test_data,
                    }
                )

            except Exception as e:
                comparison_results.append(
                    {
                        "algorithm": algorithm.to_dict(),
                        "performance": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        return (
            jsonify(
                {
                    "comparison": comparison_results,
                    "test_data": test_data,
                    "timestamp": time.time(),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"error": "Failed to compare algorithms", "details": str(e)}),
            500,
        )


@algorithms_bp.route("/seed", methods=["POST"])
def seed_algorithms():
    """Seed the database with initial algorithms (for development)"""
    try:
        # Check if algorithms already exist
        if Algorithm.query.count() > 0:
            return jsonify({"message": "Algorithms already seeded"}), 200

        # Classical algorithms
        classical_algorithms = [
            {
                "name": "RSA-2048",
                "type": "classical",
                "category": "RSA",
                "key_size": 2048,
                "description": "RSA encryption with 2048-bit key",
                "quantum_safe": False,
            },
            {
                "name": "RSA-4096",
                "type": "classical",
                "category": "RSA",
                "key_size": 4096,
                "description": "RSA encryption with 4096-bit key",
                "quantum_safe": False,
            },
            {
                "name": "ECC-P256",
                "type": "classical",
                "category": "ECC",
                "key_size": 256,
                "description": "Elliptic Curve Cryptography with P-256 curve",
                "quantum_safe": False,
            },
            {
                "name": "ECC-P384",
                "type": "classical",
                "category": "ECC",
                "key_size": 384,
                "description": "Elliptic Curve Cryptography with P-384 curve",
                "quantum_safe": False,
            },
            {
                "name": "AES-128",
                "type": "classical",
                "category": "AES",
                "key_size": 128,
                "description": "Advanced Encryption Standard with 128-bit key",
                "quantum_safe": False,
            },
            {
                "name": "AES-256",
                "type": "classical",
                "category": "AES",
                "key_size": 256,
                "description": "Advanced Encryption Standard with 256-bit key",
                "quantum_safe": False,
            },
        ]

        # Post-quantum algorithms
        post_quantum_algorithms = [
            {
                "name": "Kyber-512",
                "type": "post-quantum",
                "category": "Kyber",
                "key_size": 512,
                "description": "CRYSTALS-Kyber with security level 1",
                "quantum_safe": True,
            },
            {
                "name": "Kyber-768",
                "type": "post-quantum",
                "category": "Kyber",
                "key_size": 768,
                "description": "CRYSTALS-Kyber with security level 3",
                "quantum_safe": True,
            },
            {
                "name": "Kyber-1024",
                "type": "post-quantum",
                "category": "Kyber",
                "key_size": 1024,
                "description": "CRYSTALS-Kyber with security level 5",
                "quantum_safe": True,
            },
            {
                "name": "Dilithium-2",
                "type": "post-quantum",
                "category": "Dilithium",
                "key_size": 2,
                "description": "CRYSTALS-Dilithium with security level 2",
                "quantum_safe": True,
            },
            {
                "name": "Dilithium-3",
                "type": "post-quantum",
                "category": "Dilithium",
                "key_size": 3,
                "description": "CRYSTALS-Dilithium with security level 3",
                "quantum_safe": True,
            },
            {
                "name": "Falcon-512",
                "type": "post-quantum",
                "category": "Falcon",
                "key_size": 512,
                "description": "Falcon signature scheme with 512-bit security",
                "quantum_safe": True,
            },
            {
                "name": "Falcon-1024",
                "type": "post-quantum",
                "category": "Falcon",
                "key_size": 1024,
                "description": "Falcon signature scheme with 1024-bit security",
                "quantum_safe": True,
            },
        ]

        all_algorithms = classical_algorithms + post_quantum_algorithms

        for algo_data in all_algorithms:
            algorithm = Algorithm(**algo_data)
            db.session.add(algorithm)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully seeded {len(all_algorithms)} algorithms",
                    "classical": len(classical_algorithms),
                    "post_quantum": len(post_quantum_algorithms),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to seed algorithms", "details": str(e)}), 500
