from tinyec import registry
import secrets
from Crypto.PublicKey import RSA

def generate_RSA_keys():
    key = RSA.generate(2048)  # Generate a new RSA key pair (2048-bit)
    private_key = key.export_key()  # Export private key
    public_key = key.publickey().export_key()  # Export public key
    return private_key, public_key


def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]

curve = registry.get_curve('secp256r1')

def generateECCKeys():
    private_key = secrets.randbelow(curve.field.n)
    public_key = private_key * curve.g

    return (public_key, private_key)

def generateSymmentricKey(user1_private_key, user2_public_key):
    return user1_private_key*user2_public_key
