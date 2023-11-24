from tinyec import registry
import secrets

def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]

curve = registry.get_curve('secp256r1')

def generateECCKeys():
    private_key = secrets.randbelow(curve.field.n)
    public_key = private_key * curve.g

    return (public_key, private_key)

def generateSymmentricKey(user1_private_key, user2_public_key):
    return user1_private_key*user2_public_key
