// Base URL for your Flask backend. Make sure it matches your server's address and port.
const FLASK_BACKEND_URL = "http://127.0.0.1:5000";

// Get references to DOM elements
const websiteInput = document.getElementById('website');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const saveBtn = document.getElementById('saveBtn');
const retrieveBtn = document.getElementById('retrieveBtn');
const messageBox = document.getElementById('messageBox');
const passwordsList = document.getElementById('passwordsList'); // This will now be largely unused
const passwordsContainer = document.getElementById('passwordsContainer'); // This will now be largely unused
const togglePassword = document.getElementById('togglePassword');

// Function to display messages to the user in the popup
function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`; // Add type class for styling (success/error)
    messageBox.classList.remove('hidden'); // Make sure the message box is visible

    // Hide the message after 3 seconds
    setTimeout(() => {
        messageBox.classList.add('hidden');
    }, 3000);
}

// Function to get the current tab's URL and pre-fill the website input
async function getCurrentTabUrl() {
    try {
        // Use chrome.tabs.query to get information about the current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
            // Extract the hostname for a cleaner website display
            const url = new URL(tab.url);
            websiteInput.value = url.hostname;
        }
    } catch (error) {
        console.error("Error getting current tab URL:", error);
        websiteInput.value = "Could not get website URL";
    }
}

// Event listener for the Save Password button
saveBtn.addEventListener('click', async () => {
    const website = websiteInput.value;
    const username = usernameInput.value;
    const password = passwordInput.value;

    if (!website || !username || !password) {
        showMessage("Please fill in all fields.", "error");
        return;
    }

    try {
        const response = await fetch(`${FLASK_BACKEND_URL}/save_password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ website, username, password }),
        });

        const result = await response.json();

        if (response.ok) { // Check if the HTTP status code is in the 200 range
            showMessage(result.message, "success");
            // Clear inputs after successful save
            usernameInput.value = '';
            passwordInput.value = '';
        } else {
            // Handle server-side errors (e.g., 400, 500)
            showMessage(result.message || "Failed to save password.", "error");
        }
    } catch (error) {
        console.error('Error saving password:', error);
        showMessage("Could not connect to the backend server. Is it running?", "error");
    }
});

// Event listener for the Retrieve Passwords button
retrieveBtn.addEventListener('click', async () => {
    const passcode = prompt("Enter Unlock Passcode:");
    if (!passcode) {
        showMessage("Passcode is required to retrieve passwords.", "error");
        return;
    }

    try {
        const response = await fetch(`${FLASK_BACKEND_URL}/retrieve_passwords`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ passcode }),
        });

        const result = await response.json();

        if (response.ok) {
            if (result.success) {
                console.log("Passwords fetched from backend:", result.passwords);

                // Store passwords in chrome.storage.local before opening new tab
                await chrome.storage.local.set({ retrievedPasswords: result.passwords });
                console.log("Passwords successfully stored in chrome.storage.local.");
                
                // Attempt to open retrieve.html in a new tab
                try {
                    const retrievePageUrl = chrome.runtime.getURL('retrieve.html');
                    console.log("Attempting to open URL:", retrievePageUrl);
                    chrome.tabs.create({ url: retrievePageUrl }, (tab) => {
                        if (chrome.runtime.lastError) {
                            console.error("Error opening tab:", chrome.runtime.lastError.message);
                            showMessage(`Failed to open retrieve page: ${chrome.runtime.lastError.message}`, "error");
                        } else {
                            console.log("Tab created successfully:", tab);
                            showMessage("Opening passwords in new tab...", "success");
                            // Optionally, hide the current popup if desired
                            // window.close();
                        }
                    });
                } catch (tabError) {
                    console.error("Error with chrome.tabs.create:", tabError);
                    showMessage("An error occurred while trying to open the retrieve page.", "error");
                }

            } else {
                showMessage(result.message || "Failed to retrieve passwords.", "error");
            }
        } else {
            showMessage(result.message || "Failed to retrieve passwords (server error).", "error");
        }
    } catch (error) {
        console.error('Error retrieving passwords from backend:', error);
        showMessage("Could not connect to the backend server. Is it running?", "error");
    }
});

// Toggle password visibility
togglePassword.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    togglePassword.textContent = type === 'password' ? 'Show' : 'Hide';
});


// Call this function when the popup is loaded
document.addEventListener('DOMContentLoaded', getCurrentTabUrl);

