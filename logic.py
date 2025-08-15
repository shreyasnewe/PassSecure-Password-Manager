import psycopg2
import uuid
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# ======== DB Setup ========
# IMPORTANT: Replace these with your actual PostgreSQL credentials
DB_NAME = "passDbs"
DB_USER = "postgres"   # change if different
DB_PASSWORD = "newe"
DB_HOST = "localhost"
DB_PORT = "5432" # Or your PostgreSQL server host

conn = None # Initialize conn to None
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS manage (
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    print("Database connection and table setup successful.")
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    # Exit if database connection fails, as the application cannot function without it
    exit()

# ======== Encryption / Decryption using MAC address ========

def get_key_from_mac():
    """Generates a 32-byte AES key from the system's MAC address."""
    mac_int = uuid.getnode()
    mac_bytes = str(mac_int).encode()
    return hashlib.sha256(mac_bytes).digest()  # 32-byte AES key for AES-256

def encrypt_data(plain_text):
    """Encrypts plain text using AES in CFB mode."""
    key = get_key_from_mac()
    iv = os.urandom(16)  # Generate a random 16-byte IV for each encryption
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(plain_text.encode()) + encryptor.finalize()
    # Prepend IV to the ciphertext before base64 encoding
    return base64.b64encode(iv + encrypted).decode()

def decrypt_data(enc_text):
    """Decrypts base64 encoded ciphertext using AES in CFB mode."""
    key = get_key_from_mac()
    raw = base64.b64decode(enc_text)
    iv = raw[:16]  # Extract IV from the beginning of the raw data
    encrypted = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    return decrypted.decode()

# ======== CLI Logic ========
def save_password():
    """Prompts user for website, username, and password, then encrypts and saves them to the database."""
    website = input("Website: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if conn is None:
        print("Error: Database connection not established.")
        return

    if website and username and password:
        enc_username = encrypt_data(username)
        enc_password = encrypt_data(password)
        try:
            c.execute("INSERT INTO manage (website, username, password) VALUES (%s, %s, %s)",
                      (website, enc_username, enc_password))
            conn.commit()
            print("✅ Password saved successfully!")
        except psycopg2.Error as e:
            print(f"Error saving password: {e}")
            conn.rollback() # Rollback transaction in case of error
    else:
        print("⚠️ All fields are required.")

def retrieve_passwords():
    """Retrieves and decrypts all saved passwords from the database after a passcode check."""
    passcode = input("Enter Unlock Passcode: ")
    if passcode != "1234":
        print("❌ Incorrect passcode.")
        return

    if conn is None:
        print("Error: Database connection not established.")
        return

    try:
        c.execute("SELECT website, username, password FROM manage")
        rows = c.fetchall()

        if not rows:
            print("No saved passwords yet.")
            return

        for row in rows:
            website, enc_username, enc_password = row
            try:
                dec_username = decrypt_data(enc_username)
                dec_password = decrypt_data(enc_password)
                print(f"\n🔹 {website}")
                print(f"   Username: {dec_username}")
                print(f"   Password: {dec_password}")
            except Exception as decrypt_error:
                # Catch specific decryption errors if possible for more granular feedback
                print(f"   ❌ Could not decrypt {website} (Error: {decrypt_error}). Possible reasons: wrong machine, corrupted data.")
    except psycopg2.Error as e:
        print(f"Error retrieving passwords: {e}")

# ======== Main Menu ========
while True:
    print("\n=== Password Manager ===")
    print("1. Save new password")
    print("2. Retrieve passwords")
    print("3. Exit")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        save_password()
    elif choice == "2":
        retrieve_passwords()
    elif choice == "3":
        if conn:
            conn.close() # Close the database connection before exiting
        print("Exiting.....")
        break
    else:
        print("⚠️ Invalid choice. Try again.")

