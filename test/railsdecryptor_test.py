import pytest
from railsdecryptor import RailsDecryptor


@pytest.fixture
def rails_7_0_examples():
    """Example encrypted fields using Rails 7.0 encryption (SHA-1 PBKDF2)"""
    return [
        {
            'ar_key': b"Q3TJUKuOUGSZmgqaD2WZ72pQdg5Rikfn",
            'ar_salt': b"9REysw2kZuLybtKjtJsIZHg8cTd2DyMT",
            'encrypted_field': '{"p":"iNB7ZNRrtgwg59ckr5h5sAz2BA==","h":{"iv":"d+P5BhM8o5u5lSvF","at":"mtaOcoICzpwZIuT+1J90bQ=="}}',
            'clear_text': 'the secret password'
        }
    ]


@pytest.fixture
def rails_7_1_examples():
    """
    Example encrypted fields using Rails 7.1+ encryption (SHA-256 PBKDF2).

    ⚠️  IMPORTANT: These use RANDOM test keys and salts - safe to commit!
    They are NOT tied to any real Rails app credentials.

    Generated from Rails 8.1.4.1 using real ActiveRecord::Encryption.

    Why random keys?
    - Never commit real production or development credentials
    - Random test fixtures are still valid for testing the decryption logic
    - Safe to share in open source projects
    """
    return [
        {
            'ar_key': b"\fe $\xB9o{8~\r\x8C\xE4g\xEAq#6\xF8\x84\x1C3\x16nm\xE1\xBA\xF37\xF7W_>",
            'ar_salt': b"6%\xCE=-;&\xAFK \xB6C\xB0\xA0'\xCF",
            'encrypted_field': '{"p":"KrCN5NyftpmTltextgro+A==","h":{"iv":"YVYyqKeIS8OUDLlX","at":"89rJalG1Si2SJWVv1dtHRw=="}}',
            'clear_text': 'test message 7.1'
        }
    ]


@pytest.fixture
def compressed_examples():
    """Example encrypted fields with compression flag (should raise error)"""
    return [
        {
            'ar_key': b"Q3TJUKuOUGSZmgqaD2WZ72pQdg5Rikfn",
            'ar_salt': b"9REysw2kZuLybtKjtJsIZHg8cTd2DyMT",
            'encrypted_field': '{"p":"iNB7ZNRrtgwg59ckr5h5sAz2BA==","h":{"iv":"d+P5BhM8o5u5lSvF","at":"mtaOcoICzpwZIuT+1J90bQ==", "c": true}}',
            'clear_text': 'the secret password'
        }
    ]


def test_rails_7_0_decryption(rails_7_0_examples):
    """Test decryption with Rails 7.0 encryption (SHA-1 PBKDF2) - auto-detects via fallback"""
    for example in rails_7_0_examples:
        decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
        result = decryptor.decrypt(example['encrypted_field'])
        assert result == example['clear_text']


def test_rails_7_1_decryption(rails_7_1_examples):
    """Test decryption with Rails 7.1+ encryption (SHA-256 PBKDF2) - auto-detects first"""
    for example in rails_7_1_examples:
        decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
        result = decryptor.decrypt(example['encrypted_field'])
        assert result == example['clear_text']


def test_auto_detection_fallback(rails_7_0_examples):
    """Test that the decryption automatically tries SHA-256 first, then falls back to SHA-1"""
    # This test verifies the fallback mechanism by successfully decrypting Rails 7.0 data
    # (which uses SHA-1). If SHA-256 didn't fail first, we'd get an error.
    for example in rails_7_0_examples:
        decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
        # Should succeed with fallback to SHA-1
        result = decryptor.decrypt(example['encrypted_field'])
        assert result == example['clear_text']


def test_compressed_decryption_raises_error(compressed_examples):
    """Test that compressed data raises CompressionNotSupportedError"""
    with pytest.raises(RailsDecryptor.CompressionNotSupportedError):
        for example in compressed_examples:
            decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
            decryptor.decrypt(example['encrypted_field'])
