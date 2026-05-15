# Reinforced Security Through Dual Encryption by Multi-Layered Steganographic Approach

A secure and intelligent steganography system that combines **AES Encryption**, **Hybrid PVD-LSB Image Steganography**, **Audio Steganography**, and **Text-based Zero Width Character Encoding** to provide advanced covert communication and data protection.

---

## 📌 Project Overview

This project focuses on enhancing cybersecurity through a **multi-layered steganographic system** that securely hides encrypted information inside multiple digital media formats such as:

- 🖼️ Images
- 🎵 Audio Files
- 📄 Text Files

The system first encrypts sensitive information using **AES (Fernet)** encryption and then embeds the encrypted data into media files using advanced steganographic techniques.

The primary goal is to ensure:

- High security
- Confidentiality
- Resistance against steganalysis
- Secure communication over untrusted networks

---

## 🚀 Features

### 🔐 Dual Layer Security
- AES-based encryption using Fernet
- PBKDF2HMAC key derivation
- HMAC verification for integrity

### 🖼️ Hybrid Image Steganography
- Combines:
  - **PVD (Pixel Value Differencing)**
  - **LSB (Least Significant Bit)**
- Dynamically switches embedding technique based on image texture

### 🎵 Audio Steganography
- LSB embedding in WAV audio files
- Maintains audio quality with minimal distortion

### 📄 Text Steganography
- Uses Zero Width Characters:
  - ZWJ
  - ZWNJ
- Invisible data hiding within text

### 🌐 Web-Based Interface
- Flask-powered web application
- User-friendly UI
- Supports embedding and extraction workflows

### 📂 Multi-Carrier Support
Supports:
- PNG
- JPEG
- WAV
- TXT

### 🧩 Modular Architecture
- Easy to maintain
- Scalable for future enhancements
- Supports additional media types

---

## 🏗️ System Architecture

The system follows a modular client-server architecture built using Flask.

### Main Modules:
- Input Module
- Encryption Module
- Steganography Module
- Extraction Module
- Decryption Module
- File Handling Module
- Download Module

---

## 🛠️ Technologies Used

### Backend
- Python 3.x
- Flask

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Libraries
- OpenCV
- NumPy
- Pillow
- Cryptography
- SciPy
- SQLite3

---

## 🔒 Encryption Process

The plaintext message is encrypted using:

- AES-128 (CBC Mode)
- Fernet Encryption
- PBKDF2HMAC Key Derivation
- SHA-256 Hashing

This ensures:
- Confidentiality
- Integrity
- Tamper Detection

---

## 🧠 Steganography Techniques

### 1️⃣ Image Steganography
Hybrid:
- PVD for textured regions
- LSB for smooth regions

### 2️⃣ Audio Steganography
- LSB embedding into WAV samples

### 3️⃣ Text Steganography
- Zero Width Character Encoding

---

## 📊 Advantages

✅ Enhanced security through encryption + steganography  
✅ Multi-format carrier support  
✅ Improved imperceptibility  
✅ Better payload capacity  
✅ Resistant to statistical attacks  
✅ User-friendly web interface  
✅ Scalable and modular design  

---

## 📁 Project Structure

```bash
project/
│
├── static/
├── templates/
├── uploads/
├── outputs/
│
├── app.py
├── encryption.py
├── image_stego.py
├── audio_stego.py
├── text_stego.py
├── extraction.py
├── requirements.txt
└── README.md
