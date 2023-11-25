import os
import uuid
from utils.encryption_utils import encrypt_file, encrypt_filename
from utils.decryption_utils import decrypt_file
from utils.ecc_utils import generateECCKeys
from utils.constant_utils import *
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, render_template, send_file
import shutil


app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


#general use methods
def encrypt(files, symmetric_key=DEFAULT_KEY, upload_path=UPLOAD_PATH, encrypted_path=ENCRYPTED_PATH):
    ciphers = []
    encrypted_original_filenames = []

    for file in files:
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            encrypted_original_filenames.append(encrypt_filename(filename.encode(FORMAT), symmetric_key))
            file.save(os.path.join(upload_path, filename))
            ciphers.append(encrypt_file(os.path.join(upload_path, filename), symmetric_key))

    encrypted_file_name = encrypted_path + str(uuid.uuid4()) + ".txt"
    with open(encrypted_file_name, "wb") as file:
        for file_index in range(len(ciphers)):
            file.write(encrypted_original_filenames[file_index] + NEW_LINE)
            file.write(ciphers[file_index] + NEW_LINE)

    return encrypted_file_name

def decrypt(files, symmetric_key=DEFAULT_KEY, processed_encrypted_files_path=PROCESSED_ENCRYPTED_FILES_PATH, decrypted_path=DECRYPTED_PATH):
    for file in files:
        if file.filename == '':
            flash('No file selected for decryption')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(processed_encrypted_files_path, filename))
            print(f'Uploaded encrypted filename: {filename}')
            decrypt_file(os.path.join(processed_encrypted_files_path, filename), symmetric_key)

    decrypted_zip_file_name = decrypted_path + str(uuid.uuid4())
    decrypted_zip_file = shutil.make_archive(decrypted_zip_file_name, 'zip', processed_encrypted_files_path)

    return decrypted_zip_file_name

def clean_files():
    folders = ['decrypted_files/', 'encrypted_files/', 'processed_encrypted_files/', 'processed_files/']
    for folder in folders:
        for file in os.listdir(folder):
            os.remove(folder+file)

def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]

# routes
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index_page():
    return render_template('index.html')

@app.route("/output/")
def output_page():
    return render_template('output.html')


#Encryption routes
@app.route("/uploadenc/", methods=['GET'])
def uploadenc_page():
    return render_template('uploadenc.html')

@app.route('/uploadenc/', methods=['POST'])
def upload_images():

    clean_files()
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('file')
    encrypted_file_name = encrypt(files)

    render_template('uploadenc.html', feedback="Encrypted files successfully!")
    
    return send_file(encrypted_file_name, as_attachment=True) 


# Decryption Routes
@app.route("/uploaddec/", methods=['GET'])
def uploaddec_page():
    return render_template('uploaddec.html')

@app.route('/uploaddec/', methods=['POST'])
def upload_encrypted_files():
    
    clean_files()
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('file')
    decrypted_zip_file_name = decrypt(files=files)

    render_template('uploaddec.html', feedback="Decrpyted files successfully!")     

    return send_file(decrypted_zip_file_name + '.zip', as_attachment=True)



# Transer Routes
@app.route("/transfer/", methods=['GET'])
def provide_transfer():
    return render_template('transfer.html')

@app.route('/transfer/', methods=['POST'])
def transfer():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('file')
    print("List of files: ", files)

    #init sender and receiver
    receiver_path, sender_path = AAKASH_PATH, ASHWIN_PATH
    if request.form['user'] == "ashwin":
        receiver_path, sender_path = sender_path, receiver_path
    print(f'Sender Path = {sender_path} and receiver path = {receiver_path}')

    # genkeys
    sender_public_key, sender_private_key = generateECCKeys()
    receiver_public_key, receiver_private_key = generateECCKeys()

    print(f'Sender pub add = {sender_public_key} and sender private key = {sender_private_key}')
    print(f'Receiver pub add = {receiver_public_key} and Receiver private key = {receiver_private_key}')

    symmetric_key = compress(sender_private_key * receiver_public_key)
    print("Symmetric Key is:", symmetric_key)

    # actual transfer

    # encrypt
    encrypted_file_name = encrypt(files, symmetric_key=symmetric_key, upload_path=sender_path, encrypted_path=sender_path)
    print("Encrypted file name is:", encrypted_file_name)

    # transfer file
    shutil.copy(encrypted_file_name, receiver_path)

    #decrypt
    encrypted_file_name = receiver_path + encrypted_file_name.split('/')[-1]
    print(f'after transfer encrypted file name is {encrypted_file_name}')
    decrypt_file(encrypted_file_name, symmetric_key, process_encrypted_files_path=receiver_path)

    #delete sender files
    for file in os.listdir(sender_path):
        os.remove(sender_path+file)

    print("Transfer complete!")

    return render_template('transfer.html', feedback="Secure Transfer Successfull!")


if __name__ == "__main__":
    app.run(use_reloader=False)