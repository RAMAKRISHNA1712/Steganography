document.addEventListener("DOMContentLoaded", function() {
    // Get references to DOM elements
    const loginContainer = document.getElementById("login-container");
    const steganographyContainer = document.getElementById("steganography-container");
    const loginButton = document.getElementById("login-button");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    const steganographyTypeSelect = document.getElementById("steganography-type");
    const operationTypeSelect = document.getElementById("operation-type");
    
    const embeddingContainer = document.getElementById("embedding-container");
    const fileUploadInput = document.getElementById("file-upload");
    const messageInput = document.getElementById("message-input");
    const encryptionPasswordInput = document.getElementById("encryption-password");
    const processButton = document.getElementById("process-button");
    const embedResultContainer = document.getElementById("embed-result-container");
    const embedResultMessage = document.getElementById("embed-result-message");
    const downloadLink = document.getElementById("download-link");

    const extractionContainer = document.getElementById("extraction-container");
    const uploadStegoFileInput = document.getElementById("upload-stego-file");
    const extractPasswordInput = document.getElementById("extract-password");
    const extractButton = document.getElementById("extract-button");
    const extractionResultContainer = document.getElementById("extraction-result-container");
    const extractedMessageDisplay = document.getElementById("extracted-message");

    // Removed hardcoded API_BASE_URL, using relative paths now

    // --- Login Logic ---
    loginButton.addEventListener("click", function() {
        const username = usernameInput.value;
        const password = passwordInput.value;

        // Simple hardcoded login for demonstration
        if (username === "user" && password === "password") {
            loginContainer.style.display = "none";
            steganographyContainer.style.display = "block";
            // Default view
            embeddingContainer.style.display = "block";
            extractionContainer.style.display = "none";
            updateFileUploadAccept(); // Set initial accept types
        } else {
            alert("Invalid username or password (Hint: user/password)");
        }
    });

    // --- UI Control Logic ---
    operationTypeSelect.addEventListener("change", function() {
        if (this.value === "embed") {
            embeddingContainer.style.display = "block";
            extractionContainer.style.display = "none";
        } else if (this.value === "extract") {
            embeddingContainer.style.display = "none";
            extractionContainer.style.display = "block";
        }
        updateFileUploadAccept(); // Update accept types when operation changes
    });

    steganographyTypeSelect.addEventListener("change", updateFileUploadAccept);

    function updateFileUploadAccept() {
        const selectedType = steganographyTypeSelect.value;
        const selectedOperation = operationTypeSelect.value;
        let acceptType = "";

        if (selectedOperation === "embed") {
            if (selectedType === "image") {
                acceptType = "image/png, image/jpeg";
            } else if (selectedType === "audio") {
                acceptType = "audio/wav";
            } else if (selectedType === "text") {
                acceptType = "text/plain";
            }
            fileUploadInput.accept = acceptType;
        } else { // Extract
            // During extraction, we accept the output formats
            if (selectedType === "image") {
                acceptType = ".png"; // Output is always PNG
            } else if (selectedType === "audio") {
                acceptType = ".wav";
            } else if (selectedType === "text") {
                acceptType = ".txt";
            }
            uploadStegoFileInput.accept = acceptType;
        }
    }

    // --- Embedding Logic ---
    processButton.addEventListener("click", function() {
        const file = fileUploadInput.files[0];
        const message = messageInput.value;
        const password = encryptionPasswordInput.value;
        const type = steganographyTypeSelect.value;

        if (!file) {
            alert("Please select a carrier file.");
            return;
        }
        if (!message) {
            alert("Please enter a message to hide.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file); // Corrected key: "file"
        formData.append("message", message);
        formData.append("password", password); // Send password (even if empty)
        formData.append("type", type);

        embedResultMessage.textContent = "Processing... please wait.";
        embedResultContainer.style.display = "block";
        downloadLink.style.display = "none";

        fetch("/embed", { // Corrected endpoint: "/embed"
            method: "POST",
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                // Try to get error message from JSON response
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    // If JSON parsing fails, throw generic error
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json(); // Expect JSON response with download_url
        })
        .then(data => {
            if (data.download_url) {
                // Use the download URL provided by the backend
                downloadLink.href = data.download_url;
                // Extract filename from the URL for the download attribute
                const filename = data.download_url.substring(data.download_url.lastIndexOf("/") + 1);
                downloadLink.download = filename;
                downloadLink.style.display = "block";
                embedResultMessage.textContent = "Embedding successful!";
                // Clear inputs after success
                fileUploadInput.value = null;
                messageInput.value = "";
                encryptionPasswordInput.value = "";
            } else {
                throw new Error(data.error || "Embedding failed: No download URL received.");
            }
        })
        .catch(error => {
            console.error("Embedding error:", error);
            embedResultMessage.textContent = `Embedding error: ${error.message}`;
            downloadLink.style.display = "none";
        });
    });

    // --- Extraction Logic ---
    extractButton.addEventListener("click", function() {
        const file = uploadStegoFileInput.files[0];
        const password = extractPasswordInput.value;
        const type = steganographyTypeSelect.value; // Get type from main selector

        if (!file) {
            alert("Please select a steganographed file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file); // Corrected key: "file"
        formData.append("password", password); // Send password (even if empty)
        formData.append("type", type);

        extractedMessageDisplay.textContent = "Extracting... please wait.";
        extractionResultContainer.style.display = "block";

        fetch("/extract", { // Using relative path
            method: "POST",
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                 // Try to get error message from JSON response
                 return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    // If JSON parsing fails, throw generic error
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.message !== undefined) {
                extractedMessageDisplay.textContent = data.message;
                // Clear inputs after success
                uploadStegoFileInput.value = null;
                extractPasswordInput.value = "";
            } else {
                // Should be caught by !response.ok, but as a fallback
                extractedMessageDisplay.textContent = data.error || "Unknown extraction error.";
            }
        })
        .catch(error => {
            console.error("Extraction error:", error);
            extractedMessageDisplay.textContent = `Extraction error: ${error.message}`;
        });
    });

    // Initial setup
    updateFileUploadAccept(); // Set initial accept types based on default selection
});

