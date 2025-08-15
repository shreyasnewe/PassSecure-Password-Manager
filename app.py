import psycopg2
import uuid
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from flask import Flask, request, jsonify
from flask_cors import CORS # <--- ADDED THIS IMPORT

app = Flask(__name__)
CORS(app) # <--- ADDED THIS LINE TO ENABLE CORS FOR ALL ROUTES

# ======== Database Configuration ========
# IMPORTANT: Replace these with your actual PostgreSQL credentials
DB_NAME = "passDbs"
DB_USER = "postgres"
DB_PASSWORD = "newe"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """
    Establishes and returns a new PostgreSQL database connection.
    Raises an exception if connection fails.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise # Re-raise the exception to be caught by the Flask route's error handling

# ======== Encryption / Decryption using MAC address ========

def get_key_from_mac():
    """Generates a 32-byte AES key from the system's MAC address."""
    mac_int = uuid.getnode()
    mac_bytes = str(mac_int).encode()
    # Use SHA256 to derive a 32-byte (256-bit) key from the MAC address bytes
    return hashlib.sha256(mac_bytes).digest()

def encrypt_data(plain_text):
    """Encrypts plain text using AES in CFB mode.
    Returns base64 encoded IV + ciphertext.
    """
    key = get_key_from_mac()
    iv = os.urandom(16)  # Generate a random 16-byte IV for each encryption
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # Encrypt the plain text and append the IV to the beginning
    encrypted = encryptor.update(plain_text.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode()

def decrypt_data(enc_text):
    """Decrypts base64 encoded ciphertext using AES in CFB mode.
    Expects IV to be prepended to the ciphertext.
    """
    key = get_key_from_mac()
    raw = base64.b64decode(enc_text)
    iv = raw[:16]  # Extract IV from the first 16 bytes of the raw data
    encrypted = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    return decrypted.decode()

# ======== API Endpoints ========

@app.route('/save_password', methods=['POST'])
def save_password():
    """
    API endpoint to save a new password.
    Expects JSON with 'website', 'username', 'password'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

    website = data.get('website')
    username = data.get('username')
    password = data.get('password')

    if not all([website, username, password]):
        return jsonify({"success": False, "message": "All fields (website, username, password) are required."}), 400

    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()

        enc_username = encrypt_data(username)
        enc_password = encrypt_data(password)

        c.execute("INSERT INTO manage (website, username, password) VALUES (%s, %s, %s)",
                  (website, enc_username, enc_password))
        conn.commit()
        return jsonify({"success": True, "message": "Password saved successfully!"}), 201
    except psycopg2.Error as e:
        # Rollback in case of database error
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        # Ensure connection is closed
        if conn:
            c.close()
            conn.close()

@app.route('/retrieve_passwords', methods=['POST'])
def retrieve_passwords():
    """
    API endpoint to retrieve all saved passwords.
    Expects JSON with 'passcode'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

    passcode = data.get('passcode')
    # In a real application, the passcode should be securely handled (e.g., hashed, multi-factor)
    if passcode != "1234":
        return jsonify({"success": False, "message": "Incorrect passcode."}), 401

    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("SELECT website, username, password FROM manage")
        rows = c.fetchall()

        if not rows:
            return jsonify({"success": True, "message": "No saved passwords yet.", "passwords": []}), 200

        decrypted_passwords = []
        for website, enc_username, enc_password in rows:
            try:
                dec_username = decrypt_data(enc_username)
                dec_password = decrypt_data(enc_password)
                decrypted_passwords.append({
                    "website": website,
                    "username": dec_username,
                    "password": dec_password
                })
            except Exception as decrypt_error:
                print(f"Decryption failed for website {website}: {decrypt_error}")
                decrypted_passwords.append({
                    "website": website,
                    "username": "DECRYPTION_FAILED",
                    "password": "DECRYPTION_FAILED",
                    "error": str(decrypt_error)
                })

        return jsonify({"success": True, "passwords": decrypted_passwords}), 200
    except psycopg2.Error as e:
        return jsonify({"success": False, "message": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        if conn:
            c.close()
            conn.close()

# ======== Main Run Block ========
if __name__ == '__main__':
    # When running in production, set debug=False and use a production WSGI server (e.g., Gunicorn)
    app.run(debug=True, port=5000)
