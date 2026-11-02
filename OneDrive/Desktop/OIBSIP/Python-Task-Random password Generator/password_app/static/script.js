const lengthSlider = document.getElementById("length");
const lengthValue = document.getElementById("lengthValue");


// Update password length display
lengthSlider.addEventListener("input", function () {
    lengthValue.textContent = lengthSlider.value;
});


// Copy Password
function copyPassword() {

    const password = document.getElementById("password");
    const copyButton = document.getElementById("copyButton");

    if (!password.value) {
        return;
    }

    navigator.clipboard.writeText(password.value)
        .then(function () {

            copyButton.textContent = "✓ Copied!";

            setTimeout(function () {
                copyButton.textContent = "📋 Copy";
            }, 2000);

        })
        .catch(function () {

            copyButton.textContent = "Copy failed";

            setTimeout(function () {
                copyButton.textContent = "📋 Copy";
            }, 2000);

        });

}


// Show / Hide Password
function togglePasswordVisibility() {

    const password = document.getElementById("password");
    const toggleButton = document.getElementById("togglePassword");

    if (password.type === "password") {

        password.type = "text";
        toggleButton.textContent = "🙈";

    } else {

        password.type = "password";
        toggleButton.textContent = "👁️";

    }

}


// Check Password Strength
function checkStrength() {

    const password = document.getElementById("password").value;

    const strengthText = document.getElementById("strengthText");
    const strengthProgress = document.getElementById("strengthProgress");


    // No password generated
    if (!password) {

        strengthText.textContent = "Generate a password";
        strengthProgress.style.width = "0%";

        return;

    }


    let score = 0;


    // Password Length
    if (password.length >= 8) score++;

    if (password.length >= 12) score++;


    // Character Types
    if (/[A-Z]/.test(password)) score++;

    if (/[a-z]/.test(password)) score++;

    if (/[0-9]/.test(password)) score++;

    if (/[^A-Za-z0-9]/.test(password)) score++;


    // Weak Password
    if (score <= 2) {

        strengthText.textContent = "Weak";
        strengthProgress.style.width = "30%";
        strengthProgress.style.background = "#dc3545";

    }


    // Medium Password
    else if (score <= 4) {

        strengthText.textContent = "Medium";
        strengthProgress.style.width = "60%";
        strengthProgress.style.background = "#f0ad4e";

    }


    // Strong Password
    else {

        strengthText.textContent = "Strong";
        strengthProgress.style.width = "100%";
        strengthProgress.style.background = "#28a745";

    }

}


// Save Password to History
function savePasswordToHistory() {

    const password = document.getElementById("password").value;

    if (!password) {
        return;
    }


    // Get history from SESSION storage
    let history = JSON.parse(
        sessionStorage.getItem("passwordHistory")
    ) || [];


    // Avoid duplicate passwords
    if (!history.includes(password)) {

        history.unshift(password);

    }


    // Keep only the latest 5 passwords
    history = history.slice(0, 5);


    // Save history only for current session
    sessionStorage.setItem(
        "passwordHistory",
        JSON.stringify(history)
    );


    displayHistory();

}


// Display Password History
function displayHistory() {

    const historyList = document.getElementById("historyList");


    // Get history from SESSION storage
    const history = JSON.parse(
        sessionStorage.getItem("passwordHistory")
    ) || [];


    // No history available
    if (history.length === 0) {

        historyList.innerHTML =
            '<p class="empty-history">No passwords generated yet.</p>';

        return;

    }


    historyList.innerHTML = "";


    history.forEach(function (password) {

        const item = document.createElement("div");

        item.className = "history-item";


        // Password text
        const passwordText = document.createElement("span");

        passwordText.textContent = password;


        // Copy button for history password
        const historyCopyButton = document.createElement("button");

        historyCopyButton.textContent = "📋 Copy";

        historyCopyButton.type = "button";


        historyCopyButton.addEventListener("click", function () {

            navigator.clipboard.writeText(password)
                .then(function () {

                    historyCopyButton.textContent = "✓ Copied!";

                    setTimeout(function () {
                        historyCopyButton.textContent = "📋 Copy";
                    }, 1500);

                });

        });


        item.appendChild(passwordText);

        item.appendChild(historyCopyButton);

        historyList.appendChild(item);

    });

}


// Clear Password History
function clearHistory() {

    // Remove history from SESSION storage
    sessionStorage.removeItem("passwordHistory");

    displayHistory();

}


// Run when page loads
checkStrength();

savePasswordToHistory();

displayHistory();