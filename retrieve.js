// This script runs when retrieve.html is loaded in a new tab.

document.addEventListener('DOMContentLoaded', async () => {
    const passwordsDisplay = document.getElementById('passwordsDisplay');

    // Function to show messages in the display area
    function showDisplayMessage(message, className = 'message') {
        passwordsDisplay.innerHTML = `<p class="${className}">${message}</p>`;
    }

    // Attempt to retrieve passwords from chrome.storage.local
    try {
        const data = await chrome.storage.local.get('retrievedPasswords');
        const passwords = data.retrievedPasswords;

        console.log("Passwords retrieved from chrome.storage.local:", passwords); // Debugging log

        if (passwords && passwords.length > 0) {
            passwordsDisplay.innerHTML = ''; // Clear the "Loading..." message
            passwords.forEach(pw => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'password-item';

                // Add website, username, and password
                const websiteStrong = document.createElement('strong');
                websiteStrong.textContent = pw.website;
                itemDiv.appendChild(websiteStrong);

                const usernameP = document.createElement('p');
                usernameP.textContent = `Username: ${pw.username}`;
                itemDiv.appendChild(usernameP);

                const passwordP = document.createElement('p');
                passwordP.textContent = `Password: ${pw.password}`;
                itemDiv.appendChild(passwordP);

                // Add copy buttons for username and password
                const copyUsernameBtn = document.createElement('button');
                copyUsernameBtn.className = 'copy-button';
                copyUsernameBtn.textContent = 'Copy Username';
                copyUsernameBtn.onclick = () => copyToClipboard(pw.username, 'Username copied!');
                itemDiv.appendChild(copyUsernameBtn);

                const copyPasswordBtn = document.createElement('button');
                copyPasswordBtn.className = 'copy-button';
                copyPasswordBtn.textContent = 'Copy Password';
                copyPasswordBtn.onclick = () => copyToClipboard(pw.password, 'Password copied!');
                itemDiv.appendChild(copyPasswordBtn);

                passwordsDisplay.appendChild(itemDiv);
            });
        } else {
            showDisplayMessage('No passwords found.', 'message');
        }
    } catch (error) {
        console.error('Error retrieving passwords from storage:', error);
        showDisplayMessage('Error loading passwords. Please try again from the extension popup.', 'message error-message');
    }

    // Function to copy text to clipboard
    function copyToClipboard(text, successMessage) {
        // Fallback for document.execCommand for Chrome extension context
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            alert(successMessage); // Use alert for simplicity in new tab context
        } catch (err) {
            console.error('Failed to copy text:', err);
            alert('Failed to copy text.');
        } finally {
            document.body.removeChild(textArea);
        }
    }
});
