import base64
from utils.aes_utils import AESCipher


def encrypt_file(filename, symmetric_key):
    aes = AESCipher(symmetric_key)
    with open(filename, "rb") as imageFile:
        value = base64.b64encode(imageFile.read())

    return aes.encrypt(value)

def encrypt_filename(filename, symmetric_key):
    aes = AESCipher(symmetric_key)
    return aes.encrypt(filename)
