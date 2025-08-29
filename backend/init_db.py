"""
Database initialization script for the Quantum-Safe Cryptography Platform
"""

from app import app, db
from models import Algorithm


def init_database():
    """Initialize the database with tables and seed data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

        # Check if algorithms already exist
        if Algorithm.query.count() > 0:
            print("Algorithms already seeded in database.")
            return

        # Seed algorithms
        print("Seeding algorithms...")

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

        print(f"Successfully seeded {len(all_algorithms)} algorithms!")
        print(f"- Classical algorithms: {len(classical_algorithms)}")
        print(f"- Post-quantum algorithms: {len(post_quantum_algorithms)}")


if __name__ == "__main__":
    init_database()
