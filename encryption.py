from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

# We will use RSA, this is an asymmetric encryption algorithm (like asked)
# it will generate key pairs, encrypt and decrypt data
# public key is used to encrypt data and private key is used to decrypt data so the private key should be kept secret

_private_key: RSAPrivateKey
_public_key: RSAPublicKey


# the encoding is PEM, which is a base64 encoded format
# format is the format of the key, the private key is in the traditional OpenSSL format
def _save_key_to_file(key, filename, is_private=False):
    if is_private:
        encoding = serialization.Encoding.PEM
        format = serialization.PrivateFormat.TraditionalOpenSSL
        encryption_algorithm = serialization.NoEncryption()
        key_bytes = key.private_bytes(
            encoding = encoding,
            format = format,
            encryption_algorithm = encryption_algorithm)
    else:
        encoding = serialization.Encoding.PEM
        format = serialization.PublicFormat.SubjectPublicKeyInfo
        encryption_algorithm = serialization.NoEncryption()
        key_bytes = key.public_bytes(
            encoding = encoding,
            format = format
        )
    with open(filename, 'wb') as key_file:
        key_file.write(key_bytes)


# load keys from files
def _load_key_from_file(filename, is_private=False):
    with open(filename, 'rb') as key_file:
        if is_private:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        else:
            return serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )


# make RSA keys
def _generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def initialize_keys():
    # load the keys from file
    # if no file, generate keys
    global _private_key, _public_key
    try:
        _private_key = _load_key_from_file('private_key.pem', is_private=True)
        _public_key = _load_key_from_file('public_key.pem', is_private=False)
    except FileNotFoundError:
        _private_key, _public_key = _generate_rsa_key_pair()
        _save_key_to_file(_private_key, 'private_key.pem', is_private=True)
        _save_key_to_file(_public_key, 'public_key.pem', is_private=False)


def encrypt_data(data : str) -> str:
    encrypted_data = _public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data.hex()


def decrypt_data(encrypted_data : str) -> str:
    decrypted_data = _private_key.decrypt(
        bytes.fromhex(encrypted_data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode()

if __name__ == '__main__':
    initialize_keys()

    name = "super_admin"
    encrypt1 = encrypt_data(name)
    encrypt2 = decrypt_data(encrypt1)
    print(encrypt1)
    print(encrypt2)
