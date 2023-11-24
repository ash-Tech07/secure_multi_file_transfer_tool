import base64
from utils.aes_utils import AESCipher
from utils.constant_utils import PROCESSED_ENCRYPTED_FILES_PATH


def decrypt_file(filename, symmetric_key, process_encrypted_files_path=PROCESSED_ENCRYPTED_FILES_PATH):
    aes = AESCipher(symmetric_key)

    with open(filename, "rb") as encrypted_file:
        while True:
            encrypted_file_name = encrypted_file.readline()
            encrypted_file_content = encrypted_file.readline()
            if not encrypted_file_name or not encrypted_file_content:
                break
            
            filename = aes.decrypt(encrypted_file_name)
            filecontent = base64.b64decode(aes.decrypt(encrypted_file_content))

            with open(process_encrypted_files_path + filename, "wb") as file:
                file.write(filecontent)

