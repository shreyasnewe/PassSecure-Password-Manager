# PassSecure: A Simple & Secure Password Manager

-----

### 🚀 Project Overview

**PassSecure** is a password management system designed to securely store and retrieve your website credentials. It consists of a **Google Chrome browser extension** for the frontend, which interacts with a **Flask-based backend API**. All sensitive data (usernames and passwords) are encrypted before being stored in a PostgreSQL database, ensuring your information is not kept in plain text.

-----

### ✨ Features

  - **Automatic Website URL Detection**: The Chrome extension automatically detects the current website's URL for easy saving.
  - **Secure Storage**: Usernames and passwords are encrypted using **AES-256 (CFB mode)** and stored in a PostgreSQL database.
  - **Device-Bound Encryption**: The encryption key is derived from the **MAC address** of the host machine, tying the encrypted data to your specific device.
  - **Passcode-Protected Retrieval**: Access to saved passwords requires an **unlock passcode** for an added layer of security.
  - **New Tab Display**: Retrieved passwords are displayed in a dedicated, clean new browser tab.
  - **Copy to Clipboard**: Easily copy retrieved usernames and passwords with dedicated buttons.

-----

### 🏛️ Architecture

PassSecure operates on a client-server model:

  - **Client (Chrome Extension)**: Your browser extension, built with HTML, CSS, and JavaScript, provides the user interface. It sends HTTP requests to the backend for all password operations.
  - **Server (Flask Backend)**: A Python Flask application handles API requests, performs the encryption/decryption of data, and manages interactions with the database.
  - **Database (PostgreSQL)**: The persistent storage for all your encrypted credentials.

-----

### 💻 Technical Stack

  - **Frontend**: HTML, CSS (Tailwind CSS), JavaScript, Chrome Extension API
  - **Backend**: Python, Flask, Flask-CORS
  - **Database**: PostgreSQL, Psycopg2
  - **Encryption**: `cryptography` library (AES-256-CFB)

-----

### ⚙️ Installation and Setup

Follow these steps to get PassSecure up and running on your local machine.

#### Prerequisites

  - Python 3.x
  - PostgreSQL Database (ensure it's installed and running)
  - Google Chrome Browser

#### 1\. Backend Setup

First, let's get the server running.

  - **Create `app.py`**: Save the Flask backend code into a file named `app.py`.
  - **Install Python Dependencies**: Navigate to your backend directory in the terminal and install the required libraries:
    ```bash
    pip install Flask psycopg2-binary cryptography Flask-CORS
    ```
  - **Configure Database Connection**: Open `app.py` and update the following variables with your PostgreSQL database credentials.
    ```python
    DB_NAME = "your_database_name"
    DB_USER = "your_username"
    DB_PASSWORD = "your_password"
    DB_HOST = "localhost" # or your PostgreSQL server host
    DB_PORT = "5432" # default PostgreSQL port
    ```
  - **Run the Flask Backend**: Start the Flask development server from your terminal:
    ```bash
    python app.py
    ```
    You should see output similar to `* Running on http://127.0.0.1:5000/`. Keep this terminal open while using the extension.

#### 2\. Chrome Extension Setup

Next, we'll set up the frontend.

  - **Create Extension Folder**: Create a new, empty folder on your computer (e.g., `PassSecure_Extension`).
  - **Save Extension Files**: Place the `manifest.json`, `popup.html`, `popup.js`, `retrieve.html`, and `retrieve.js` files inside your `PassSecure_Extension` folder.
  - **Load in Chrome**:
    1.  Open your Chrome browser and go to `chrome://extensions/`.
    2.  Enable **Developer mode** (toggle switch in the top-right corner).
    3.  Click the **"Load unpacked"** button.
    4.  Select the `PassSecure_Extension` folder you created.
  - **Pin the Extension (Optional)**: For easy access, click the puzzle piece icon in your Chrome toolbar, and then click the pin icon next to "Simple PassSecure".

-----

### 🚀 Usage

Ensure your Flask backend (`app.py`) is running before using the extension.

#### Saving a New Password

1.  **Navigate**: Go to the website for which you want to save credentials.
2.  **Open Extension**: Click the PassSecure extension icon in your Chrome toolbar.
3.  **Input**: The "Website URL" field should auto-populate. Enter your **Username** and **Password**.
4.  **Save**: Click the "Save Password" button. A success message will confirm the save.

#### Retrieving Passwords

1.  **Open Extension**: Click the PassSecure extension icon.
2.  **Click Retrieve**: Click the "Retrieve Passwords" button.
3.  **Enter Passcode**: A prompt will appear. Enter the default unlock passcode: `1234`.
4.  **View**: If the passcode is correct, a new Chrome tab will open displaying all your saved credentials.
5.  **Copy**: Use the "Copy Username" and "Copy Password" buttons to quickly copy the respective credentials to your clipboard.

-----

### ⚠️ Security Considerations

This project is a functional demonstration for **educational purposes**. For a production-grade password manager, critical security enhancements are necessary:

  - **Master Password Strength**: The current passcode `1234` is highly insecure. A real application would implement robust master password hashing with salting and key derivation functions (e.g., PBKDF2, Argon2).
  - **Key Management**: While MAC address-based key derivation ties data to a machine, more advanced key management strategies (e.g., derived from a strong master password, encrypted key files) would be needed for portability and higher security.
  - **CORS Configuration**: The current `CORS(app)` in Flask enables CORS for all origins. In production, this should be restricted to only trusted origins.
  - **Error Handling and Logging**: More sophisticated error handling and secure logging practices are required to prevent information leakage.
  - **Auditing and Penetration Testing**: A real-world application would undergo rigorous security audits.
