import pytest
from railsdecryptor import RailsDecryptor

@pytest.fixture
def examples():
    return [
        {
            'ar_key': b"Q3TJUKuOUGSZmgqaD2WZ72pQdg5Rikfn",
            'ar_salt': b"9REysw2kZuLybtKjtJsIZHg8cTd2DyMT",
            'encrypted_field': '{"p":"iNB7ZNRrtgwg59ckr5h5sAz2BA==","h":{"iv":"d+P5BhM8o5u5lSvF","at":"mtaOcoICzpwZIuT+1J90bQ=="}}',
            'clear_text': 'the secret password'
        }
    ]

@pytest.fixture
def compressed_examples():
    return [
        {
            'ar_key': b"Q3TJUKuOUGSZmgqaD2WZ72pQdg5Rikfn",
            'ar_salt': b"9REysw2kZuLybtKjtJsIZHg8cTd2DyMT",
            'encrypted_field': '{"p":"iNB7ZNRrtgwg59ckr5h5sAz2BA==","h":{"iv":"d+P5BhM8o5u5lSvF","at":"mtaOcoICzpwZIuT+1J90bQ==", "c": true}}',
            'clear_text': 'the secret password'
        }
    ]

def test_basic_decryption(examples):
    #     active_record_encryption_primary_key,
    #     active_record_encryption_key_derivation_salt,
    #     example1
    # ):
    for example in examples:
        decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
        result = decryptor.decrypt(example['encrypted_field'])
        assert result == example['clear_text']

def test_compressed_decryption(compressed_examples):
    with pytest.raises(RailsDecryptor.CompressionNotSupportedError):
        #     active_record_encryption_primary_key,
        #     active_record_encryption_key_derivation_salt,
        #     example1
        # ):
        for example in compressed_examples:
            decryptor = RailsDecryptor(example['ar_key'], example['ar_salt'])
            result = decryptor.decrypt(example['encrypted_field'])
            # assert result == example['clear_text']  <== NOPE
