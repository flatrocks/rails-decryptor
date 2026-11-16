"""
Rails ActiveRecord Encryption field decryption utility.
Supports Rails 7.0 (SHA-1) and Rails 7.1+ (SHA-256) encryption methods.
"""
import json
from collections import namedtuple
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA1, SHA256
from Crypto.Protocol.KDF import PBKDF2

__version_info__ = ('0', '0', '0')
__version__ = '.'.join(__version_info__)


class RailsDecryptor:
    """
    Decrypts encrypted Rails data fields.

    Supports both Rails 7.0 (SHA-1 based PBKDF2) and Rails 7.1+ (SHA-256 based PBKDF2).
    Does not support compression. See README.md for details.
    """
    EncryptedObject = namedtuple("RailsEncryptedField", ["ciphertext", "nonce", "tag", "compressed"])

    class CompressionNotSupportedError(Exception):
        """Indicates that unsupported data compression was encountered"""
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    def __init__(self, password, salt):
        """
        Initialize the decryptor.

        Args:
            password: Rails ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY
            salt: Rails ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT
        """
        self.password = password
        self.salt = salt

    def decrypt(self, raw_text_field):
        """
        Decrypt a Rails encrypted field.

        Tries Rails 7.1+ (SHA-256) first, then falls back to Rails 7.0 (SHA-1) if needed.
        """
        encrypted_object = self._encrypted_object(raw_text_field)

        if not encrypted_object.compressed is False:
            raise RailsDecryptor.CompressionNotSupportedError(
                "Compressed data detected, but compression is not supported by RailsDecryptor"
            )

        # Try 7.1+ (SHA-256) first
        try:
            key = self._derive_key(self.password, self.salt, hash_algorithm="SHA256")
            cipher = AES.new(key, AES.MODE_GCM, encrypted_object.nonce)
            return cipher.decrypt_and_verify(encrypted_object.ciphertext, encrypted_object.tag).decode()
        except ValueError:
            # Fallback to 7.0 (SHA-1)
            key = self._derive_key(self.password, self.salt, hash_algorithm="SHA1")
            cipher = AES.new(key, AES.MODE_GCM, encrypted_object.nonce)
            return cipher.decrypt_and_verify(encrypted_object.ciphertext, encrypted_object.tag).decode()

    def _derive_key(self, password, salt, hash_algorithm="SHA256"):
        """
        Derive the encryption key from password and salt using PBKDF2.

        Args:
            password: The password/key material
            salt: The salt
            hash_algorithm: Either "SHA1" or "SHA256"
        """
        hash_module = SHA1 if hash_algorithm == "SHA1" else SHA256
        return PBKDF2(password, salt, 32, count=2**16, hmac_hash_module=hash_module)

    def _encrypted_object(self, raw_text_field):
        """
        Parse a Rails encrypted value.

        A Rails encrypted value is stored as a JSON-encoded string:
        {"p": payload, "h": {"iv": init-vector(nonce), "at": tag}}
        All values are base64 encoded.
        """
        encrypted_object = json.loads(raw_text_field)
        return RailsDecryptor.EncryptedObject(
            ciphertext=b64decode(encrypted_object["p"]),
            nonce=b64decode(encrypted_object["h"]["iv"]),
            tag=b64decode(encrypted_object["h"]["at"]),
            compressed=encrypted_object["h"].get("c", False)
        )
