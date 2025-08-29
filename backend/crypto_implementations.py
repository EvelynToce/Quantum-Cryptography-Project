"""
Cryptographic algorithm implementations for the Quantum-Safe Cryptography Platform.
This module provides implementations for both classical and post-quantum cryptographic algorithms.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES as CryptoAES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os
import json
from abc import ABC, abstractmethod


class CryptoBase(ABC):
    """Base class for all cryptographic implementations"""

    def __init__(self, key_size):
        self.key_size = key_size
        self.public_key = None
        self.private_key = None

    @abstractmethod
    def generate_keys(self):
        """Generate public/private key pair"""
        pass

    @abstractmethod
    def encrypt(self, plaintext):
        """Encrypt plaintext"""
        pass

    @abstractmethod
    def decrypt(self, ciphertext):
        """Decrypt ciphertext"""
        pass


class RSACrypto(CryptoBase):
    """RSA cryptographic implementation"""

    def generate_keys(self):
        """Generate RSA key pair"""
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=self.key_size, backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

            # Serialize keys for storage/transmission
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return {
                "public_key": base64.b64encode(public_pem).decode("utf-8"),
                "private_key": base64.b64encode(private_pem).decode("utf-8"),
                "key_size": self.key_size,
            }
        except Exception as e:
            raise Exception(f"RSA key generation failed: {str(e)}")

    def encrypt(self, plaintext):
        """Encrypt using RSA"""
        try:
            if not self.public_key:
                self.generate_keys()

            # Convert string to bytes
            if isinstance(plaintext, str):
                plaintext = plaintext.encode("utf-8")

            # RSA encryption with OAEP padding
            ciphertext = self.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            return base64.b64encode(ciphertext).decode("utf-8")
        except Exception as e:
            raise Exception(f"RSA encryption failed: {str(e)}")

    def decrypt(self, ciphertext):
        """Decrypt using RSA"""
        try:
            if not self.private_key:
                raise Exception("Private key not available for decryption")

            # Decode base64 ciphertext
            ciphertext_bytes = base64.b64decode(ciphertext.encode("utf-8"))

            # RSA decryption
            plaintext = self.private_key.decrypt(
                ciphertext_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            return plaintext.decode("utf-8")
        except Exception as e:
            raise Exception(f"RSA decryption failed: {str(e)}")


class ECCCrypto(CryptoBase):
    """Elliptic Curve Cryptography implementation"""

    def __init__(self, key_size):
        super().__init__(key_size)
        # Map key sizes to curves
        self.curve_map = {256: ec.SECP256R1(), 384: ec.SECP384R1(), 521: ec.SECP521R1()}
        self.curve = self.curve_map.get(key_size, ec.SECP256R1())

    def generate_keys(self):
        """Generate ECC key pair"""
        try:
            self.private_key = ec.generate_private_key(self.curve, default_backend())
            self.public_key = self.private_key.public_key()

            # Serialize keys
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return {
                "public_key": base64.b64encode(public_pem).decode("utf-8"),
                "private_key": base64.b64encode(private_pem).decode("utf-8"),
                "curve": self.curve.name,
                "key_size": self.key_size,
            }
        except Exception as e:
            raise Exception(f"ECC key generation failed: {str(e)}")

    def sign(self, message):
        """Sign message using ECC"""
        try:
            if not self.private_key:
                self.generate_keys()

            if isinstance(message, str):
                message = message.encode("utf-8")

            signature = self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))

            return base64.b64encode(signature).decode("utf-8")
        except Exception as e:
            raise Exception(f"ECC signing failed: {str(e)}")

    def verify(self, message, signature):
        """Verify ECC signature"""
        try:
            if not self.public_key:
                raise Exception("Public key not available for verification")

            if isinstance(message, str):
                message = message.encode("utf-8")

            signature_bytes = base64.b64decode(signature.encode("utf-8"))

            try:
                self.public_key.verify(
                    signature_bytes, message, ec.ECDSA(hashes.SHA256())
                )
                return True
            except:
                return False
        except Exception as e:
            raise Exception(f"ECC verification failed: {str(e)}")

    def encrypt(self, plaintext):
        """ECC encryption (using ECIES-like approach with AES)"""
        try:
            if not self.public_key:
                self.generate_keys()

            # Generate ephemeral key pair
            ephemeral_private_key = ec.generate_private_key(
                self.curve, default_backend()
            )
            ephemeral_public_key = ephemeral_private_key.public_key()

            # Perform ECDH to get shared secret
            shared_key = ephemeral_private_key.exchange(ec.ECDH(), self.public_key)

            # Derive AES key from shared secret
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(shared_key)
            aes_key = digest.finalize()[:32]  # Use first 32 bytes for AES-256

            # Encrypt with AES
            if isinstance(plaintext, str):
                plaintext = plaintext.encode("utf-8")

            iv = os.urandom(16)
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Pad plaintext to block size
            padded_plaintext = plaintext + b" " * (16 - len(plaintext) % 16)
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

            # Serialize ephemeral public key
            ephemeral_public_pem = ephemeral_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            result = {
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
                "ephemeral_public_key": base64.b64encode(ephemeral_public_pem).decode(
                    "utf-8"
                ),
            }

            return json.dumps(result)
        except Exception as e:
            raise Exception(f"ECC encryption failed: {str(e)}")

    def decrypt(self, encrypted_data):
        """ECC decryption"""
        try:
            if not self.private_key:
                raise Exception("Private key not available for decryption")

            # Parse encrypted data
            data = json.loads(encrypted_data)
            ciphertext = base64.b64decode(data["ciphertext"])
            iv = base64.b64decode(data["iv"])
            ephemeral_public_pem = base64.b64decode(data["ephemeral_public_key"])

            # Deserialize ephemeral public key
            ephemeral_public_key = serialization.load_pem_public_key(
                ephemeral_public_pem, backend=default_backend()
            )

            # Perform ECDH to get shared secret
            shared_key = self.private_key.exchange(ec.ECDH(), ephemeral_public_key)

            # Derive AES key from shared secret
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(shared_key)
            aes_key = digest.finalize()[:32]

            # Decrypt with AES
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            plaintext = padded_plaintext.rstrip(b" ")

            return plaintext.decode("utf-8")
        except Exception as e:
            raise Exception(f"ECC decryption failed: {str(e)}")


class AESCrypto(CryptoBase):
    """AES symmetric encryption implementation"""

    def generate_keys(self):
        """Generate AES key"""
        try:
            self.key = get_random_bytes(self.key_size // 8)  # Convert bits to bytes

            return {
                "key": base64.b64encode(self.key).decode("utf-8"),
                "key_size": self.key_size,
            }
        except Exception as e:
            raise Exception(f"AES key generation failed: {str(e)}")

    def encrypt(self, plaintext):
        """Encrypt using AES"""
        try:
            if not hasattr(self, "key"):
                self.generate_keys()

            if isinstance(plaintext, str):
                plaintext = plaintext.encode("utf-8")

            # Generate random IV
            iv = get_random_bytes(16)

            # Create cipher
            cipher = CryptoAES.new(self.key, CryptoAES.MODE_CBC, iv)

            # Pad plaintext and encrypt
            padded_plaintext = pad(plaintext, CryptoAES.block_size)
            ciphertext = cipher.encrypt(padded_plaintext)

            result = {
                "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                "iv": base64.b64encode(iv).decode("utf-8"),
            }

            return json.dumps(result)
        except Exception as e:
            raise Exception(f"AES encryption failed: {str(e)}")

    def decrypt(self, encrypted_data):
        """Decrypt using AES"""
        try:
            if not hasattr(self, "key"):
                raise Exception("AES key not available for decryption")

            # Parse encrypted data
            data = json.loads(encrypted_data)
            ciphertext = base64.b64decode(data["ciphertext"])
            iv = base64.b64decode(data["iv"])

            # Create cipher and decrypt
            cipher = CryptoAES.new(self.key, CryptoAES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ciphertext)

            # Remove padding
            plaintext = unpad(padded_plaintext, CryptoAES.block_size)

            return plaintext.decode("utf-8")
        except Exception as e:
            raise Exception(f"AES decryption failed: {str(e)}")


# Post-Quantum Cryptography Implementations (Simplified/Mock implementations)
# Note: These are simplified implementations for demonstration purposes.
# In production, you would use proper PQC libraries like liboqs or pqcrypto.


class KyberCrypto(CryptoBase):
    """CRYSTALS-Kyber post-quantum KEM implementation (simplified)"""

    def generate_keys(self):
        """Generate Kyber key pair (mock implementation)"""
        try:
            # Mock key generation - in reality, this would use proper Kyber implementation
            public_key_size = {512: 800, 768: 1184, 1024: 1568}.get(self.key_size, 800)
            private_key_size = {512: 1632, 768: 2400, 1024: 3168}.get(
                self.key_size, 1632
            )

            self.public_key = get_random_bytes(public_key_size)
            self.private_key = get_random_bytes(private_key_size)

            return {
                "public_key": base64.b64encode(self.public_key).decode("utf-8"),
                "private_key": base64.b64encode(self.private_key).decode("utf-8"),
                "algorithm": "Kyber",
                "security_level": self.key_size,
                "public_key_size": len(self.public_key),
                "private_key_size": len(self.private_key),
            }
        except Exception as e:
            raise Exception(f"Kyber key generation failed: {str(e)}")

    def encrypt(self, plaintext):
        """Kyber encryption (mock implementation using AES)"""
        try:
            if not self.public_key:
                self.generate_keys()

            # Mock: Use AES for actual encryption with derived key
            shared_secret = get_random_bytes(32)  # Mock shared secret

            # Encrypt plaintext with AES using shared secret
            aes_crypto = AESCrypto(256)
            aes_crypto.key = shared_secret
            encrypted_message = aes_crypto.encrypt(plaintext)

            # Mock encapsulated shared secret
            encapsulated_secret = get_random_bytes(64)  # Mock encapsulation

            result = {
                "encapsulated_secret": base64.b64encode(encapsulated_secret).decode(
                    "utf-8"
                ),
                "encrypted_message": encrypted_message,
                "algorithm": "Kyber",
            }

            return json.dumps(result)
        except Exception as e:
            raise Exception(f"Kyber encryption failed: {str(e)}")

    def decrypt(self, encrypted_data):
        """Kyber decryption (mock implementation)"""
        try:
            if not self.private_key:
                raise Exception("Private key not available for decryption")

            data = json.loads(encrypted_data)
            encapsulated_secret = base64.b64decode(data["encapsulated_secret"])
            encrypted_message = data["encrypted_message"]

            # Mock: Derive shared secret from encapsulated secret
            shared_secret = get_random_bytes(32)  # Mock decapsulation

            # Decrypt message with AES
            aes_crypto = AESCrypto(256)
            aes_crypto.key = shared_secret
            plaintext = aes_crypto.decrypt(encrypted_message)

            return plaintext
        except Exception as e:
            raise Exception(f"Kyber decryption failed: {str(e)}")


class DilithiumCrypto(CryptoBase):
    """CRYSTALS-Dilithium post-quantum signature implementation (simplified)"""

    def generate_keys(self):
        """Generate Dilithium key pair (mock implementation)"""
        try:
            # Mock key sizes based on security level
            key_sizes = {
                2: {"public": 1312, "private": 2528},
                3: {"public": 1952, "private": 4000},
                5: {"public": 2592, "private": 4864},
            }

            sizes = key_sizes.get(self.key_size, key_sizes[2])

            self.public_key = get_random_bytes(sizes["public"])
            self.private_key = get_random_bytes(sizes["private"])

            return {
                "public_key": base64.b64encode(self.public_key).decode("utf-8"),
                "private_key": base64.b64encode(self.private_key).decode("utf-8"),
                "algorithm": "Dilithium",
                "security_level": self.key_size,
                "public_key_size": len(self.public_key),
                "private_key_size": len(self.private_key),
            }
        except Exception as e:
            raise Exception(f"Dilithium key generation failed: {str(e)}")

    def sign(self, message):
        """Dilithium signing (mock implementation)"""
        try:
            if not self.private_key:
                self.generate_keys()

            if isinstance(message, str):
                message = message.encode("utf-8")

            # Mock signature generation
            signature_size = {2: 2420, 3: 3293, 5: 4595}.get(self.key_size, 2420)
            signature = get_random_bytes(signature_size)

            result = {
                "signature": base64.b64encode(signature).decode("utf-8"),
                "message_hash": base64.b64encode(
                    hashes.Hash(hashes.SHA256(), default_backend()).finalize()
                ).decode("utf-8"),
                "algorithm": "Dilithium",
            }

            return json.dumps(result)
        except Exception as e:
            raise Exception(f"Dilithium signing failed: {str(e)}")

    def verify(self, message, signature_data):
        """Dilithium verification (mock implementation)"""
        try:
            if not self.public_key:
                raise Exception("Public key not available for verification")

            # Mock verification - always returns True for valid format
            data = json.loads(signature_data)
            return "signature" in data and "algorithm" in data
        except Exception as e:
            raise Exception(f"Dilithium verification failed: {str(e)}")

    def encrypt(self, plaintext):
        """Dilithium is a signature scheme, not encryption. Use hybrid approach."""
        raise Exception(
            "Dilithium is a signature algorithm, not for encryption. Use sign() method instead."
        )

    def decrypt(self, ciphertext):
        """Dilithium is a signature scheme, not encryption."""
        raise Exception(
            "Dilithium is a signature algorithm, not for decryption. Use verify() method instead."
        )


class FalconCrypto(CryptoBase):
    """Falcon post-quantum signature implementation (simplified)"""

    def generate_keys(self):
        """Generate Falcon key pair (mock implementation)"""
        try:
            # Mock key sizes
            key_sizes = {
                512: {"public": 897, "private": 1281},
                1024: {"public": 1793, "private": 2305},
            }

            sizes = key_sizes.get(self.key_size, key_sizes[512])

            self.public_key = get_random_bytes(sizes["public"])
            self.private_key = get_random_bytes(sizes["private"])

            return {
                "public_key": base64.b64encode(self.public_key).decode("utf-8"),
                "private_key": base64.b64encode(self.private_key).decode("utf-8"),
                "algorithm": "Falcon",
                "security_level": self.key_size,
                "public_key_size": len(self.public_key),
                "private_key_size": len(self.private_key),
            }
        except Exception as e:
            raise Exception(f"Falcon key generation failed: {str(e)}")

    def sign(self, message):
        """Falcon signing (mock implementation)"""
        try:
            if not self.private_key:
                self.generate_keys()

            if isinstance(message, str):
                message = message.encode("utf-8")

            # Mock signature (Falcon signatures are variable length, average sizes)
            signature_size = {512: 690, 1024: 1330}.get(self.key_size, 690)
            signature = get_random_bytes(signature_size)

            result = {
                "signature": base64.b64encode(signature).decode("utf-8"),
                "message_hash": base64.b64encode(
                    hashes.Hash(hashes.SHA256(), default_backend()).finalize()
                ).decode("utf-8"),
                "algorithm": "Falcon",
            }

            return json.dumps(result)
        except Exception as e:
            raise Exception(f"Falcon signing failed: {str(e)}")

    def verify(self, message, signature_data):
        """Falcon verification (mock implementation)"""
        try:
            if not self.public_key:
                raise Exception("Public key not available for verification")

            # Mock verification
            data = json.loads(signature_data)
            return "signature" in data and "algorithm" in data
        except Exception as e:
            raise Exception(f"Falcon verification failed: {str(e)}")

    def encrypt(self, plaintext):
        """Falcon is a signature scheme, not encryption."""
        raise Exception(
            "Falcon is a signature algorithm, not for encryption. Use sign() method instead."
        )

    def decrypt(self, ciphertext):
        """Falcon is a signature scheme, not encryption."""
        raise Exception(
            "Falcon is a signature algorithm, not for decryption. Use verify() method instead."
        )
