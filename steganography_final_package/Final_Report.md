# Steganography Web Application: Final Report

## 1. Introduction and Project Goal

This report details the development, debugging, and finalization of the Steganography Web Application. The primary goal of this project, as outlined in the initial requirements, was to create a web-based tool capable of embedding and extracting secret text messages within various carrier file types: images (PNG/JPEG), audio (WAV), and text (TXT). A key requirement was to ensure the application is compatible with and deployable on a Windows operating system. The application utilizes the Least Significant Bit (LSB) steganography technique for hiding data and incorporates optional password-based encryption (using Fernet symmetric encryption derived from PBKDF2) to secure the hidden messages.

The project involved inheriting partially completed code, diagnosing and fixing critical bugs in the core steganography logic, implementing missing features for audio and text steganography, refining the backend API, correcting the frontend interface, and thoroughly testing the complete functionality.

## 2. Technology Stack

The application employs the following technologies:

*   **Backend:** Python 3, utilizing the Flask web framework to handle HTTP requests, manage file uploads/downloads, and orchestrate the steganography processes.
*   **Steganography & File Handling:**
    *   **Image:** Pillow (PIL fork) library for image loading, pixel manipulation (LSB), and saving.
    *   **Audio:** Python's built-in `wave` module and the `numpy` library for reading/writing WAV file samples and performing LSB manipulation.
    *   **Text:** Python's built-in string manipulation and file I/O, using Zero-Width Characters (ZWNJ/ZWJ) for embedding data.
    *   **File System:** Python's `os` module for path manipulation, ensuring cross-platform compatibility (especially for Windows paths using `os.path.join`).
*   **Encryption:** The `cryptography` library is used for robust, password-based symmetric encryption. Specifically, PBKDF2HMAC with SHA256 is used for key derivation from the user's password and a random salt, and Fernet (AES in CBC mode with PKCS7 padding) is used for the actual encryption/decryption.
*   **Frontend:** Standard web technologies - HTML for structure, CSS for styling, and JavaScript for user interaction, handling form submissions via Fetch API calls to the Flask backend, and dynamically updating the UI.
*   **Development Server:** Flask's built-in development server.
*   **Dependencies:** All necessary Python libraries are listed in the `requirements.txt` file.

## 3. Features Implemented

The final application successfully implements the following features:

*   **Unified Web Interface:** A single-page web application allowing users to select the steganography type (image, audio, text) and operation (embed, extract).
*   **Image Steganography:**
    *   Embeds text messages into PNG or JPEG images (output is always PNG to preserve LSB data).
    *   Extracts hidden messages from steganographed PNG images.
*   **Audio Steganography:**
    *   Embeds text messages into WAV audio files.
    *   Extracts hidden messages from steganographed WAV files.
*   **Text Steganography:**
    *   Embeds text messages into TXT files using zero-width characters.
    *   Extracts hidden messages from steganographed TXT files.
*   **Optional Encryption:** Users can provide a password during embedding to encrypt the message before hiding it. The same password is required for successful extraction and decryption.
*   **File Handling:** Secure handling of file uploads and providing download links for generated steganographed files.
*   **Dynamic UI:** The user interface updates dynamically based on the selected steganography type and operation, showing relevant options and input fields.

## 4. Debugging and Fixes Summary

The initial phase of the project focused heavily on debugging the core steganography logic inherited from the previous state. The primary challenges and the fixes implemented include:

*   **Extraction Logic Overhaul:** The original extraction functions (`extract_lsb`, `extract_audio_lsb`, `extract_text`) suffered from critical bugs related to reading the embedded message length and correctly reconstructing the data bits. This led to `UnicodeDecodeError` for unencrypted messages and incorrect encryption flag detection for encrypted ones. The functions were rewritten multiple times, culminating in a robust single-loop approach. This final version first reads the 32-bit length prefix, calculates the total bits needed, and then reads all required LSBs (length + data) in a single pass before converting the relevant data bits into bytes. This resolved the data corruption and flag detection issues.
*   **Embedding Logic Correction:** A subtle bug was found and fixed in the original `embed_lsb` function where the data index wasn't incremented correctly after embedding each bit, causing data corruption during embedding itself.
*   **Syntax Errors:** Several persistent f-string syntax errors within the Python code were identified and corrected.
*   **Frontend API Interaction:** The JavaScript code (`script.js`) was updated to use correct relative API endpoint paths (`/embed`, `/extract`, `/download/...`) instead of hardcoded local URLs. The form data keys used in `fetch` calls were corrected to match the keys expected by the Flask backend (`file` instead of `file0`). Response handling was improved to correctly process JSON responses for download URLs and extracted messages, as well as displaying backend errors more effectively.
*   **Server Configuration:** The Flask application was configured to serve the `index.html` file correctly from the root path and to listen on `0.0.0.0` to be accessible within the network environment.

## 5. Windows Setup and Running Instructions

This application is designed to run on a Windows machine. Follow these steps:

1.  **Install Python:** Download and install the latest stable version of Python 3 from [python.org](https://www.python.org/). **Important:** During installation, ensure you check the box labeled "Add Python to PATH".

2.  **Extract Project Files:** Unzip the provided project archive (`steganography_project.zip` or similar) into a folder of your choice (e.g., `C:\Projects\SteganographyApp`).

3.  **Open Command Prompt:** Open the Windows Command Prompt (cmd.exe). You can search for "cmd" in the Windows search bar.

4.  **Navigate to Project Directory:** Use the `cd` command to navigate into the project directory where you extracted the files. Specifically, go into the `steganography` sub-directory which contains `app.py`.
    ```bash
    cd C:\Projects\SteganographyApp\steganography
    ```

5.  **Create Virtual Environment:** It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects. Create one using `venv`:
    ```bash
    python -m venv venv
    ```

6.  **Activate Virtual Environment:** Activate the newly created environment. The command differs slightly depending on your shell (Command Prompt vs. PowerShell).
    *   **Command Prompt:**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **PowerShell:**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
        (If you encounter an execution policy error in PowerShell, you might need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first and confirm).
    You'll know the environment is active because `(venv)` will appear at the beginning of your command prompt line.

7.  **Install Dependencies:** Install all the required Python libraries listed in `requirements.txt` using pip:
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, Pillow, numpy, cryptography, etc.

8.  **Run the Application:** Start the Flask development server:
    ```bash
    python app.py
    ```

9.  **Access the Application:** The command prompt will show output indicating the server is running, typically including lines like:
    ```
     * Running on http://127.0.0.1:5500
    ```
    Open your web browser (like Chrome, Firefox, or Edge) and navigate to `http://127.0.0.1:5500`. You should see the application's login page.

10. **Login:** Use the default credentials (Username: `user`, Password: `password`) to log in and access the steganography features.

11. **Stopping the Application:** To stop the server, go back to the command prompt where it's running and press `Ctrl + C`.

12. **Deactivating Virtual Environment:** When you are finished working on the project, you can deactivate the virtual environment by simply typing:
    ```bash
    deactivate
    ```

## 6. Usage Guide

1.  **Login:** Access the application via `http://127.0.0.1:5500` and log in using the credentials `user` / `password`.
2.  **Select Type:** Choose the type of steganography you want to perform (Image, Audio, or Text) from the dropdown menu.
3.  **Select Operation:** Choose whether you want to `Embed` a message or `Extract` a message.
4.  **Embedding:**
    *   Ensure `Embed` is selected.
    *   Click "Select Carrier File" and choose the appropriate file type (PNG/JPEG for Image, WAV for Audio, TXT for Text).
    *   Enter the secret message you want to hide in the "Message" text area.
    *   (Optional) Enter a password in the "Encryption Password" field if you want to encrypt the message.
    *   Click the "Embed Message" button.
    *   Wait for the process to complete. A download link for the steganographed file will appear.
5.  **Extraction:**
    *   Ensure `Extract` is selected.
    *   Click "Select Steganographed File" and choose the file containing the hidden message (the output file from the embedding step - .png, .wav, or .txt).
    *   If the message was embedded with a password, enter the *exact same* password in the "Decryption Password" field.
    *   Click the "Extract Message" button.
    *   Wait for the process to complete. The extracted message will be displayed in the text area below.

## 7. Limitations and Future Improvements

*   **LSB Vulnerability:** The LSB technique used is simple but not very robust against steganalysis (detection) or image/audio compression (especially lossy formats like JPEG, though the output is forced to PNG for images).
*   **Capacity:** LSB has limited data hiding capacity. Embedding very large messages may require large carrier files or risk noticeable degradation.
*   **Text Steganography Method:** The zero-width character method used for text is simple but can be fragile. Some text editors or systems might strip these characters. Other methods (like synonym substitution or format-based methods) could be explored.
*   **Frontend Robustness:** The frontend provides basic functionality but could be enhanced with better progress indicators, more specific error messages, and potentially previews for images.
*   **Security:** The hardcoded login is for demonstration only. A real application would require a proper authentication system.
*   **Deployment:** While compatible with Windows, deployment to a production Windows server (like IIS) requires additional configuration (e.g., using a production WSGI server like Waitress or Gunicorn, and potentially configuring IIS with wfastcgi or HttpPlatformHandler).
*   **Hybrid Techniques:** Implementing more advanced techniques like hybrid LSB/PVD for images could improve capacity and robustness.

## 8. Conclusion

The Steganography Web Application project successfully met its core objectives. Critical bugs in the existing code were identified and resolved, missing features for audio and text steganography were implemented, and optional encryption was added. The application was thoroughly tested and verified to work correctly for all supported file types and operations. The final codebase and instructions are prepared for deployment on a Windows system.

