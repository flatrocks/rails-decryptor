"""
asdf
"""
import json
from collections import namedtuple
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA1
from Crypto.Protocol.KDF import PBKDF2
# just for version, test modes

__version_info__ = ('0', '0', '0')
__version__ = '.'.join(__version_info__)


class RailsDecryptor:
    """
    Decrypts encrypted Rails data fields.

    DOES NOT support compression (the default.) See README.md for details.
    """
    EncryptedObject = namedtuple("RailsEncryptedField", ["ciphertext", "nonce", "tag", "compressed"])

    class CompressionNotSupportedError(Exception):
        """Indicates that unsupported data compression was encountered"""
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    def __init__(
            self,
            password,
            salt):
        self.key = self._key(password, salt)


    def decrypt(self, raw_text_field):
        """ Decrypt a Rails encrypted field
        """
        encrypted_object = self._encrypted_object(raw_text_field)

        if not encrypted_object.compressed is False:
            raise RailsDecryptor.CompressionNotSupportedError("Compressed data detected, but compression is not supported by RailsDecryptor")

        cipher = AES.new(self.key, AES.MODE_GCM, encrypted_object.nonce)
        return cipher.decrypt_and_verify(encrypted_object.ciphertext, encrypted_object.tag).decode()


    def _key(self, password, salt):
        """ The actual encryption key is derived from password and salt
        where password is Rails ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY
        and salt is Rails ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT
        """
        return PBKDF2(password, salt, 32, count=2**16, hmac_hash_module=SHA1)


    def _encrypted_object(self, raw_text_field):
        """ A Rails encrypted value is stored as json-encoded string:
        {"p": payload, "h": {"iv": init-vector(nonce), "at": tag}}
        and all the values are base64 encoded.
        """
        encrypted_object = json.loads(raw_text_field)
        return RailsDecryptor.EncryptedObject(
            ciphertext=b64decode(encrypted_object["p"]),
            nonce=b64decode(encrypted_object["h"]["iv"]),
            tag=b64decode(encrypted_object["h"]["at"]),
            compressed=encrypted_object["h"].get("c", False)
        )
