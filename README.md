# rails-decryptor

Python module to decrypt Rails 7+ encrypted fields using non-deterministic encryption.

**Version 1.0.0** - Now supports both Rails 7.0 and Rails 7.1+ with automatic version detection!

## Features

- ✅ **Dual Version Support**: Automatically detects and decrypts both Rails 7.0 (SHA-1) and Rails 7.1+ (SHA-256) encrypted fields
- ✅ **Zero Configuration**: No need to specify which Rails version encrypted the data - it just works
- ✅ **Fast Fallback**: Tries Rails 7.1+ first, falls back to Rails 7.0 if needed
- ✅ **Comprehensive Testing**: Fully tested with real Rails 8.1 generated encryption
- ✅ **Production Ready**: Used in production environments

## Quick Start

### Installation

```bash
pip install railsdecryptor
```

### Basic Usage

```python
from railsdecryptor import RailsDecryptor

# Create decryptor (works for both Rails 7.0 and 7.1+)
decryptor = RailsDecryptor(ar_primary_key, ar_salt)

# Decrypt any Rails encrypted field
plaintext = decryptor.decrypt(encrypted_field_json)
```

### In Your Rails Model

```ruby
# Define the encrypted field with compression disabled
encrypts :password, encryptor: ActiveRecord::Encryption::Encryptor.new(compress: false)
```

Then access it from Python:

```python
from railsdecryptor import RailsDecryptor

# Same code works for Rails 7.0 and 7.1+
decryptor = RailsDecryptor(
    your_ar_primary_key,
    your_ar_salt
)
decrypted_password = decryptor.decrypt(encrypted_field_json)
print(decrypted_password)
```

## How It Works

### Rails Encryption Versions

This module supports both Rails encryption versions:

| Rails Version | PBKDF2 Hash | Iterations | Key Length |
|---|---|---|---|
| 7.0 | SHA-1 | 2^16 (65536) | 32 bytes |
| 7.1+ | SHA-256 | 2^16 (65536) | 32 bytes |

### Auto-Detection Mechanism

When you call `decrypt()`:

1. **First**: Tries SHA-256 based PBKDF2 key derivation (Rails 7.1+)
2. **If that fails**: Automatically falls back to SHA-1 (Rails 7.0)
3. **Returns**: Decrypted message if either method succeeds
4. **If both fail**: Raises `ValueError`

This means you don't need to know which Rails version encrypted the data—the decryptor figures it out automatically.

```python
# Same code works for both Rails versions!
decryptor = RailsDecryptor(key, salt)
result = decryptor.decrypt(encrypted_field)  # Works for 7.0 or 7.1+
```

### Why No Version Parameter?

Previously, you had to specify the Rails version:

```python
# Old way (deprecated)
decryptor = RailsDecryptor(key, salt, rails_version="7.0")
```

Now it's automatic:

```python
# New way (1.0.0+)
decryptor = RailsDecryptor(key, salt)  # Auto-detects!
```

The new approach is simpler and handles mixed encryption versions transparently.

## Important: Compression Support

⚠️ **This module does NOT support compression.**

Rails compresses long encrypted messages by default. When defining encrypted fields, **always disable compression**:

```ruby
# ✓ CORRECT - Compression disabled
encrypts :password, encryptor: ActiveRecord::Encryption::Encryptor.new(compress: false)

# ✗ WRONG - Will fail
encrypts :password  # Uses default compression!
```

If you try to decrypt a compressed message, you'll get:

```
railsdecryptor.RailsDecryptor.CompressionNotSupportedError: 
  Compressed data detected, but compression is not supported by RailsDecryptor
```

You can tell if a message is compressed by checking the JSON structure:

```json
{
  "p": "...",
  "h": {
    "iv": "...",
    "at": "...",
    "c": true      ← This flag means compressed
  }
}
```

## Testing

The module includes comprehensive tests covering:

- ✓ Rails 7.0 decryption (SHA-1 based PBKDF2)
- ✓ Rails 7.1+ decryption (SHA-256 based PBKDF2)
- ✓ Auto-detection fallback mechanism
- ✓ Compression error handling

Run tests:

```bash
pytest test/railsdecryptor_test.py -v
```

All tests use **random encryption keys** (safe to commit to version control, not tied to any real credentials).

## Migration from Earlier Versions

If you were using an earlier version that required a `rails_version` parameter:

```python
# Old code (no longer works)
decryptor = RailsDecryptor(key, salt, rails_version="7.0")

# New code (1.0.0+)
decryptor = RailsDecryptor(key, salt)  # Auto-detects version
```

Simply remove the `rails_version` parameter. The decryptor will automatically detect which encryption method was used.

## Performance Considerations

- **Rails 7.1+ data**: 1 key derivation + 1 AES decryption
- **Rails 7.0 data**: 2 key derivations + 2 AES attempts (the fallback)

Performance impact is minimal:
- PBKDF2 with 2^16 iterations is fast (~10ms on modern hardware)
- Fallback only occurs for Rails 7.0 messages
- Typical usage patterns cache the decryptor instance

## Troubleshooting

### ValueError: MAC check failed

Both decryption attempts failed. This means:
- Wrong key or salt
- Data is corrupted
- Data was encrypted with an unsupported method

### CompressionNotSupportedError

The encrypted field has compression enabled. Disable it in your Rails model:

```ruby
encrypts :your_field, encryptor: ActiveRecord::Encryption::Encryptor.new(compress: false)
```

Then re-encrypt the data.

### Performance is slow

If decrypting Rails 7.0 data seems slow, it's the double key derivation. This is expected and normal. If you have a known data set that's all one version, you could optimize by:

```python
# Cache the decryptor instance
decryptor = RailsDecryptor(key, salt)

# Reuse it for multiple decryptions
for encrypted_field in encrypted_fields:
    plaintext = decryptor.decrypt(encrypted_field)
```

## Technical Details

### Key Derivation

Both Rails versions use PBKDF2 for key derivation with identical parameters except the hash algorithm:

```python
PBKDF2(
    password=primary_key,
    salt=key_derivation_salt,
    dkLen=32,
    count=2**16,
    hmac_hash_module=SHA1 or SHA256  # ← Only difference
)
```

The derived key is used with AES-256-GCM for encryption/decryption.

### Fallback Implementation

The fallback mechanism uses exception handling:

```python
try:
    # Try Rails 7.1+ (SHA-256)
    key = derive_key(password, salt, "SHA256")
    return decrypt_with_key(key, encrypted_object)
except ValueError:
    # Fallback to Rails 7.0 (SHA-1)
    key = derive_key(password, salt, "SHA1")
    return decrypt_with_key(key, encrypted_object)
```

This is safe because AES-GCM MAC verification only succeeds with the correct key.

## Related Testing Documentation

For detailed information about generating test fixtures, see [GENERATE_TEST_DATA.md](GENERATE_TEST_DATA.md).

## License

See [LICENSE](LICENSE) file for details.
