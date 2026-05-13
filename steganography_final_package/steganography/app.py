
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io
import math
import wave
import numpy as np
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import traceback
import re # For text steganography

# Define static folder correctly
app = Flask(__name__, static_folder="static") 
CORS(app)

# Configure folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "steganographed_files"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Encryption/Decryption Functions ---
def generate_key(password, salt=None):
    """Generate a key from password and salt using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    # Key needs to be base64 encoded for Fernet
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_message(message, password):
    """Encrypt a message using Fernet symmetric encryption."""
    if not password:
        # Return original message bytes if no password
        return message.encode("utf-8"), None 
    
    key, salt = generate_key(password)
    f = Fernet(key)
    encrypted_data = f.encrypt(message.encode("utf-8"))
    # Return salt along with encrypted data
    return encrypted_data, salt

def decrypt_message(encrypted_data, password, salt):
    """Decrypt a message using Fernet symmetric encryption."""
    if not password or salt is None:
        # Attempt to decode as UTF-8 if no password/salt provided (assume unencrypted)
        try:
            return encrypted_data.decode("utf-8")
        except UnicodeDecodeError:
             # If decoding fails, return an error message
             raise ValueError("Error: Could not decode data. It might be encrypted or corrupted.")
    
    key, _ = generate_key(password, salt)
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")
    except Exception as e: # Catch potential decryption errors (e.g., InvalidToken)
        print(f"Decryption error: {e}")
        raise ValueError("Decryption failed. Password might be incorrect or data corrupted.")

# --- Helper Function to convert data to binary ---
def data_to_binary(data):
    """Convert data to binary format."""
    if isinstance(data, str):
        # Ensure string is encoded to bytes first (UTF-8 recommended)
        data = data.encode("utf-8") 
    if isinstance(data, bytes) or isinstance(data, bytearray):
        return "".join(format(byte, "08b") for byte in data)
    elif isinstance(data, int) or isinstance(data, float):
        # Handle potential floats by converting to int first
        return format(int(data), "08b") 
    else:
        raise TypeError("Unsupported data type for binary conversion")

# --- Image Steganography (LSB) ---
def embed_lsb(image_path, message, password=None):
    """
    Embeds a message into an image using Least Significant Bit (LSB) steganography.
    Optionally encrypts the message if a password is provided.
    Returns the path to the steganographed image and the full binary data embedded.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        pixels = list(img.getdata())
        
        encrypted_data, salt = encrypt_message(message, password)
        
        if salt is not None:
            data_to_embed = b"\x01" + salt + encrypted_data
            print(f"[DEBUG Embed] Encrypted case: data_to_embed length = {len(data_to_embed)} bytes")
        else:
            data_to_embed = b"\x00" + encrypted_data
            print(f"[DEBUG Embed] Unencrypted case: data_to_embed length = {len(data_to_embed)} bytes")
        
        binary_data = data_to_binary(data_to_embed)
        print(f"[DEBUG Embed] binary_data length = {len(binary_data)} bits")
        data_len = len(binary_data)
        
        length_binary = format(data_len, "032b")
        binary_data_with_prefix = length_binary + binary_data # Renamed for clarity
        total_bits = len(binary_data_with_prefix)
        
        # Corrected f-string using single quotes inside
        print(f"[Embed] Data to embed: {'Encrypted' if salt else 'Unencrypted'} message") 
        print(f"[Embed] Original message: {message[:50]}...")
        print(f"[Embed] Data bytes (flag+salt+msg): {data_to_embed.hex()[:100]}...")
        print(f"[Embed] Binary data length (bits): {data_len}")
        print(f"[Embed] Total binary data (incl. length prefix): {total_bits} bits")
        print(f"[Embed] Image size: {width}x{height} pixels")
        
        max_capacity = width * height * 3
        if total_bits > max_capacity:
            raise ValueError(f"Error: Message too large for image. Required bits: {total_bits}, Max capacity: {max_capacity}")
            
        modified_pixels = []
        data_index = 0
        
        for pixel_idx, pixel in enumerate(pixels):
            r, g, b = pixel
            new_r, new_g, new_b = r, g, b
            
            if data_index < total_bits:
                new_r = (r & 0xFE) | int(binary_data_with_prefix[data_index])
                data_index += 1
            
            if data_index < total_bits:
                new_g = (g & 0xFE) | int(binary_data_with_prefix[data_index])
                data_index += 1
                
            if data_index < total_bits:
                new_b = (b & 0xFE) | int(binary_data_with_prefix[data_index])
                data_index += 1
                
            modified_pixels.append((new_r, new_g, new_b))
            
            if data_index >= total_bits:
                modified_pixels.extend(pixels[pixel_idx + 1:])
                break
        
        modified_img = Image.new(img.mode, img.size)
        modified_img.putdata(modified_pixels)
        
        base_filename = secure_filename(os.path.basename(image_path))
        name, ext = os.path.splitext(base_filename)
        steganographed_image_path = os.path.join(app.config["OUTPUT_FOLDER"], f"stego_{name}.png") 
        modified_img.save(steganographed_image_path, "PNG")
        print(f"[Embed] Steganographed image saved to: {steganographed_image_path}")
        # Return the binary data *with* prefix for testing comparison
        return steganographed_image_path, binary_data_with_prefix 
        
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        raise ValueError(f"Input image file not found: {image_path}")
    except ValueError as ve:
        print(ve)
        raise
    except Exception as e:
        print(f"Error during LSB embedding: {e}")
        traceback.print_exc()
        raise ValueError("An unexpected error occurred during image embedding.")

def extract_lsb(image_path, password=None):
    """
    Extracts a message from an image using LSB steganography.
    (Rewritten version 4 - Single loop extraction)
    """
    try:
        img = Image.open(image_path).convert("RGB")
        pixels = list(img.getdata())
        
        # First, determine how many bits we *might* need to read for the length
        temp_bits = []
        pixel_index = 0
        while len(temp_bits) < 32 and pixel_index < len(pixels):
            r, g, b = pixels[pixel_index]
            temp_bits.append(str(r & 1))
            temp_bits.append(str(g & 1))
            temp_bits.append(str(b & 1))
            pixel_index += 1
            
        if len(temp_bits) < 32:
            raise ValueError("Error: Not enough pixels to extract message length.")
            
        length_str = "".join(temp_bits[:32])
        try:
            data_length = int(length_str, 2)
        except ValueError:
             raise ValueError(f"Error: Invalid length string extracted: {length_str}")
             
        print(f"[Extract] Extracted embedded data length (bits): {data_length}")
        
        if data_length == 0:
            return "" # No message embedded
            
        total_bits_to_extract = 32 + data_length
        max_capacity = len(pixels) * 3
        if total_bits_to_extract > max_capacity:
            raise ValueError(f"Error: Declared data length ({data_length}) exceeds image capacity ({max_capacity}). Corrupted data?")

        # Now, extract *all* required bits in one go
        all_bits = []
        pixel_index = 0
        bits_extracted_count = 0
        while bits_extracted_count < total_bits_to_extract and pixel_index < len(pixels):
            r, g, b = pixels[pixel_index]
            if bits_extracted_count < total_bits_to_extract:
                all_bits.append(str(r & 1))
                bits_extracted_count += 1
            if bits_extracted_count < total_bits_to_extract:
                all_bits.append(str(g & 1))
                bits_extracted_count += 1
            if bits_extracted_count < total_bits_to_extract:
                all_bits.append(str(b & 1))
                bits_extracted_count += 1
            pixel_index += 1

        if bits_extracted_count < total_bits_to_extract:
             raise ValueError(f"Error: Could only extract {bits_extracted_count} of {total_bits_to_extract} total bits needed.")

        # Process the extracted bits
        binary_data_str = "".join(all_bits)
        # Verify length prefix matches what we calculated earlier (sanity check)
        extracted_length_str = binary_data_str[:32]
        if extracted_length_str != length_str:
             # This should ideally not happen if the single loop worked correctly
             raise ValueError("Internal Error: Length prefix mismatch during extraction.")
             
        data_bits_str = binary_data_str[32:]
        print(f"[Extract] Extracted data bits string (first 100): {data_bits_str[:100]}...")
        
        # Convert data bits string to bytes
        if len(data_bits_str) != data_length:
             # This check is important
             raise ValueError(f"Error: Length mismatch after extraction. Expected {data_length} data bits, got {len(data_bits_str)}.")
        if len(data_bits_str) % 8 != 0:
            raise ValueError("Error: Extracted data bit length is not a multiple of 8.")
            
        extracted_bytes = bytearray()
        for i in range(0, len(data_bits_str), 8):
            byte_str = data_bits_str[i:i+8]
            try:
                extracted_bytes.append(int(byte_str, 2))
            except ValueError:
                 raise ValueError(f"Error converting byte string to int: {byte_str}")
            
        print(f"[Extract] Converted bytes (hex): {extracted_bytes.hex()[:100]}...")
        
        # Process data based on encryption flag
        if len(extracted_bytes) == 0:
             raise ValueError("Error: No data bytes extracted despite non-zero length.")

        encryption_flag = extracted_bytes[0]
        print(f"[Extract] Encryption flag: {encryption_flag}")
        
        if encryption_flag == 1:
            print("[Extract] Encryption flag detected.")
            if not password:
                raise ValueError("Error: Message is encrypted. Please provide the password.")
            if len(extracted_bytes) < 17: # 1 byte flag + 16 bytes salt
                raise ValueError("Error: Encrypted data too short for salt.")
            salt = bytes(extracted_bytes[1:17])
            encrypted_data = bytes(extracted_bytes[17:])
            print(f"[Extract] Extracted salt: {salt.hex()}")
            print(f"[Extract] Encrypted data (hex): {encrypted_data.hex()[:100]}...")
            decrypted_message = decrypt_message(encrypted_data, password, salt)
            print(f"[Extract] Decrypted message: {decrypted_message[:100]}...")
            return decrypted_message
        elif encryption_flag == 0:
            print("[Extract] No encryption flag detected.")
            message_bytes = bytes(extracted_bytes[1:])
            print(f"[Extract] Message bytes (hex): {message_bytes.hex()[:100]}...")
            try:
                decoded_message = message_bytes.decode("utf-8")
                print(f"[Extract] Decoded message: {decoded_message[:100]}...")
                return decoded_message
            except UnicodeDecodeError as e:
                print(f"[Extract] UnicodeDecodeError: {e}")
                raise ValueError("Error: Could not decode message using UTF-8. Possible data corruption.")
        else:
            raise ValueError(f"Error: Invalid encryption flag found: {encryption_flag}")

    except FileNotFoundError:
        raise ValueError("Error: Steganographed file not found.")
    except ValueError as ve:
        raise
    except Exception as e:
        print(f"Error during LSB extraction: {e}")
        traceback.print_exc()
        raise ValueError("Error: An unexpected error occurred during extraction.")

# --- Audio Steganography (LSB) ---
def embed_audio_lsb(audio_path, message, password=None):
    """
    Embeds a message into a WAV audio file using LSB steganography.
    """
    try:
        with wave.open(audio_path, "rb") as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()
            frames = wav.readframes(n_frames)
            
        if sample_width == 1:
            dtype = np.uint8
        elif sample_width == 2:
            dtype = np.int16
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")
            
        samples = np.frombuffer(frames, dtype=dtype).copy()
        
        encrypted_data, salt = encrypt_message(message, password)
        
        if salt is not None:
            data_to_embed = b"\x01" + salt + encrypted_data
        else:
            data_to_embed = b"\x00" + encrypted_data
            
        binary_data = data_to_binary(data_to_embed)
        data_len = len(binary_data)
        length_binary = format(data_len, "032b")
        binary_data_with_prefix = length_binary + binary_data
        total_bits = len(binary_data_with_prefix)
        
        print(f"[Embed Audio] Total binary data (incl. length prefix): {total_bits} bits")
        print(f"[Embed Audio] Number of samples: {len(samples)}")
        
        max_capacity = len(samples)
        if total_bits > max_capacity:
            raise ValueError(f"Error: Message too large for audio. Required bits: {total_bits}, Max capacity: {max_capacity}")
            
        data_index = 0
        for i in range(len(samples)):
            if data_index < total_bits:
                sample = samples[i]
                # Modify LSB of the sample
                samples[i] = (sample & ~1) | int(binary_data_with_prefix[data_index])
                data_index += 1
            else:
                break
                
        modified_frames = samples.tobytes()
        
        base_filename = secure_filename(os.path.basename(audio_path))
        name, ext = os.path.splitext(base_filename)
        steganographed_audio_path = os.path.join(app.config["OUTPUT_FOLDER"], f"stego_{name}.wav")
        
        with wave.open(steganographed_audio_path, "wb") as wav_out:
            wav_out.setnchannels(n_channels)
            wav_out.setsampwidth(sample_width)
            wav_out.setframerate(framerate)
            wav_out.writeframes(modified_frames)
            
        print(f"[Embed Audio] Steganographed audio saved to: {steganographed_audio_path}")
        return steganographed_audio_path
        
    except FileNotFoundError:
        raise ValueError(f"Input audio file not found: {audio_path}")
    except ValueError as ve:
        raise
    except Exception as e:
        print(f"Error during audio LSB embedding: {e}")
        traceback.print_exc()
        raise ValueError("An unexpected error occurred during audio embedding.")

def extract_audio_lsb(audio_path, password=None):
    """
    Extracts a message from a WAV audio file using LSB steganography.
    (Rewritten version 4 - Single loop extraction)
    """
    try:
        with wave.open(audio_path, "rb") as wav:
            sample_width = wav.getsampwidth()
            n_frames = wav.getnframes()
            frames = wav.readframes(n_frames)
            
        if sample_width == 1:
            dtype = np.uint8
        elif sample_width == 2:
            dtype = np.int16
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")
            
        samples = np.frombuffer(frames, dtype=dtype)
        
        # First, determine how many bits we *might* need to read for the length
        temp_bits = []
        sample_index = 0
        while len(temp_bits) < 32 and sample_index < len(samples):
            sample = samples[sample_index]
            temp_bits.append(str(sample & 1))
            sample_index += 1
            
        if len(temp_bits) < 32:
            raise ValueError("Error: Not enough samples to extract message length.")
            
        length_str = "".join(temp_bits[:32])
        try:
            data_length = int(length_str, 2)
        except ValueError:
             raise ValueError(f"Error: Invalid length string extracted: {length_str}")
             
        print(f"[Extract Audio] Extracted embedded data length (bits): {data_length}")
        
        if data_length == 0:
            return "" # No message embedded
            
        total_bits_to_extract = 32 + data_length
        max_capacity = len(samples)
        if total_bits_to_extract > max_capacity:
            raise ValueError(f"Error: Declared data length ({data_length}) exceeds audio capacity ({max_capacity}). Corrupted data?")

        # Now, extract *all* required bits in one go
        all_bits = []
        sample_index = 0
        bits_extracted_count = 0
        while bits_extracted_count < total_bits_to_extract and sample_index < len(samples):
            sample = samples[sample_index]
            all_bits.append(str(sample & 1))
            bits_extracted_count += 1
            sample_index += 1

        if bits_extracted_count < total_bits_to_extract:
             raise ValueError(f"Error: Could only extract {bits_extracted_count} of {total_bits_to_extract} total bits needed.")

        # Process the extracted bits
        binary_data_str = "".join(all_bits)
        extracted_length_str = binary_data_str[:32]
        if extracted_length_str != length_str:
             raise ValueError("Internal Error: Length prefix mismatch during audio extraction.")
             
        data_bits_str = binary_data_str[32:]
        print(f"[Extract Audio] Extracted data bits string (first 100): {data_bits_str[:100]}...")
        
        # Convert data bits string to bytes
        if len(data_bits_str) != data_length:
             raise ValueError(f"Error: Length mismatch after audio extraction. Expected {data_length} data bits, got {len(data_bits_str)}.")
        if len(data_bits_str) % 8 != 0:
            raise ValueError("Error: Extracted audio data bit length is not a multiple of 8.")
            
        extracted_bytes = bytearray()
        for i in range(0, len(data_bits_str), 8):
            byte_str = data_bits_str[i:i+8]
            try:
                extracted_bytes.append(int(byte_str, 2))
            except ValueError:
                 raise ValueError(f"Error converting audio byte string to int: {byte_str}")
            
        print(f"[Extract Audio] Converted bytes (hex): {extracted_bytes.hex()[:100]}...")
        
        # Process data based on encryption flag
        if len(extracted_bytes) == 0:
             raise ValueError("Error: No data bytes extracted from audio despite non-zero length.")

        encryption_flag = extracted_bytes[0]
        print(f"[Extract Audio] Encryption flag: {encryption_flag}")
        
        if encryption_flag == 1:
            print("[Extract Audio] Encryption flag detected.")
            if not password:
                raise ValueError("Error: Audio message is encrypted. Please provide the password.")
            if len(extracted_bytes) < 17:
                raise ValueError("Error: Encrypted audio data too short for salt.")
            salt = bytes(extracted_bytes[1:17])
            encrypted_data = bytes(extracted_bytes[17:])
            decrypted_message = decrypt_message(encrypted_data, password, salt)
            return decrypted_message
        elif encryption_flag == 0:
            print("[Extract Audio] No encryption flag detected.")
            message_bytes = bytes(extracted_bytes[1:])
            try:
                decoded_message = message_bytes.decode("utf-8")
                return decoded_message
            except UnicodeDecodeError as e:
                raise ValueError("Error: Could not decode audio message using UTF-8. Possible data corruption.")
        else:
            raise ValueError(f"Error: Invalid encryption flag found in audio: {encryption_flag}")

    except FileNotFoundError:
        raise ValueError("Error: Steganographed audio file not found.")
    except ValueError as ve:
        raise
    except Exception as e:
        print(f"Error during audio LSB extraction: {e}")
        traceback.print_exc()
        raise ValueError("Error: An unexpected error occurred during audio extraction.")

# --- Text Steganography (Using Zero-Width Characters) ---
# Simple method: Encode bits using Zero-Width Non-Joiner (ZWNJ - U+200C) for 0 and Zero-Width Joiner (ZWJ - U+200D) for 1
ZWNJ = "\u200c"
ZWJ = "\u200d"

def embed_text(text_content, message, password=None):
    """
    Embeds a message into text using zero-width characters.
    """
    try:
        encrypted_data, salt = encrypt_message(message, password)
        
        if salt is not None:
            data_to_embed = b"\x01" + salt + encrypted_data
        else:
            data_to_embed = b"\x00" + encrypted_data
            
        binary_data = data_to_binary(data_to_embed)
        data_len = len(binary_data)
        length_binary = format(data_len, "032b")
        binary_data_with_prefix = length_binary + binary_data
        
        print(f"[Embed Text] Total binary data (incl. length prefix): {len(binary_data_with_prefix)} bits")
        
        zero_width_encoded = "".join([ZWNJ if bit == "0" else ZWJ for bit in binary_data_with_prefix])
        
        # Embed at the beginning of the text content
        steganographed_text = zero_width_encoded + text_content
        
        return steganographed_text
        
    except Exception as e:
        print(f"Error during text embedding: {e}")
        traceback.print_exc()
        raise ValueError("An unexpected error occurred during text embedding.")

def extract_text(text_content, password=None):
    """
    Extracts a message hidden in text using zero-width characters.
    (Rewritten version 4 - Single loop extraction concept)
    """
    try:
        # Find all zero-width characters at the beginning
        zero_width_chars = ""
        for char in text_content:
            if char == ZWNJ or char == ZWJ:
                zero_width_chars += char
            else:
                # Stop as soon as a non-zero-width character is found
                break 
        
        if len(zero_width_chars) < 32:
            raise ValueError("Error: No hidden message found or data too short for length.")
            
        # Extract length bits
        length_binary_str = "".join(["0" if char == ZWNJ else "1" for char in zero_width_chars[:32]])
        try:
            data_length = int(length_binary_str, 2)
        except ValueError:
            raise ValueError(f"Error: Invalid length string extracted from text: {length_binary_str}")
            
        print(f"[Extract Text] Extracted embedded data length (bits): {data_length}")
        
        if data_length == 0:
            return "" # No message embedded
            
        total_bits_to_extract = 32 + data_length
        
        if len(zero_width_chars) < total_bits_to_extract:
            raise ValueError(f"Error: Found only {len(zero_width_chars)} zero-width chars, need {total_bits_to_extract} for declared length.")
            
        # Extract all relevant zero-width characters
        relevant_zero_width_chars = zero_width_chars[:total_bits_to_extract]
        
        # Convert to binary string
        binary_data_str = "".join(["0" if char == ZWNJ else "1" for char in relevant_zero_width_chars])
        
        # Sanity check length prefix
        extracted_length_str = binary_data_str[:32]
        if extracted_length_str != length_binary_str:
             raise ValueError("Internal Error: Length prefix mismatch during text extraction.")
             
        data_bits_str = binary_data_str[32:]
        print(f"[Extract Text] Extracted data bits string (first 100): {data_bits_str[:100]}...")
        
        # Convert data bits string to bytes
        if len(data_bits_str) != data_length:
             raise ValueError(f"Error: Length mismatch after text extraction. Expected {data_length} data bits, got {len(data_bits_str)}.")
        if len(data_bits_str) % 8 != 0:
            raise ValueError("Error: Extracted text data bit length is not a multiple of 8.")
            
        extracted_bytes = bytearray()
        for i in range(0, len(data_bits_str), 8):
            byte_str = data_bits_str[i:i+8]
            try:
                extracted_bytes.append(int(byte_str, 2))
            except ValueError:
                 raise ValueError(f"Error converting text byte string to int: {byte_str}")
            
        print(f"[Extract Text] Converted bytes (hex): {extracted_bytes.hex()[:100]}...")
        
        # Process data based on encryption flag
        if len(extracted_bytes) == 0:
             raise ValueError("Error: No data bytes extracted from text despite non-zero length.")

        encryption_flag = extracted_bytes[0]
        print(f"[Extract Text] Encryption flag: {encryption_flag}")
        
        if encryption_flag == 1:
            print("[Extract Text] Encryption flag detected.")
            if not password:
                raise ValueError("Error: Text message is encrypted. Please provide the password.")
            if len(extracted_bytes) < 17:
                raise ValueError("Error: Encrypted text data too short for salt.")
            salt = bytes(extracted_bytes[1:17])
            encrypted_data = bytes(extracted_bytes[17:])
            decrypted_message = decrypt_message(encrypted_data, password, salt)
            return decrypted_message
        elif encryption_flag == 0:
            print("[Extract Text] No encryption flag detected.")
            message_bytes = bytes(extracted_bytes[1:])
            try:
                decoded_message = message_bytes.decode("utf-8")
                return decoded_message
            except UnicodeDecodeError as e:
                raise ValueError("Error: Could not decode text message using UTF-8. Possible data corruption.")
        else:
            raise ValueError(f"Error: Invalid encryption flag found in text: {encryption_flag}")

    except ValueError as ve:
        raise
    except Exception as e:
        print(f"Error during text extraction: {e}")
        traceback.print_exc()
        raise ValueError("Error: An unexpected error occurred during text extraction.")

# --- Flask Routes ---
@app.route("/")
def index():
    # Serve index.html from the static folder
    return send_from_directory(app.static_folder, "index.html")

@app.route("/embed", methods=["POST"])
def embed():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        message = request.form.get("message", "")
        password = request.form.get("password", None)
        stego_type = request.form.get("type", "image") # image, audio, text
        
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        if not message:
             return jsonify({"error": "Message cannot be empty"}), 400

        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)
        
        output_path = None
        steganographed_text_content = None

        if stego_type == "image":
            # Pass password to embed_lsb, it handles encryption internally
            output_path, _ = embed_lsb(upload_path, message, password)
        elif stego_type == "audio":
            if not filename.lower().endswith(".wav"):
                 return jsonify({"error": "Only .wav audio files are supported for embedding."}), 400
            output_path = embed_audio_lsb(upload_path, message, password)
        elif stego_type == "text":
            if not filename.lower().endswith(".txt"):
                 return jsonify({"error": "Only .txt files are supported for text embedding."}), 400
            with open(upload_path, "r", encoding="utf-8") as f:
                original_text = f.read()
            steganographed_text_content = embed_text(original_text, message, password)
            # Save the modified text to a file for download
            base_filename = secure_filename(os.path.basename(upload_path))
            name, ext = os.path.splitext(base_filename)
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], f"stego_{name}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(steganographed_text_content)
        else:
            return jsonify({"error": "Invalid steganography type specified"}), 400

        # Clean up uploaded file
        # os.remove(upload_path)
        
        # Return the path for download
        return jsonify({"download_url": f"/download/{os.path.basename(output_path)}"})

    except ValueError as ve:
        # os.remove(upload_path) # Clean up upload on error
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # os.remove(upload_path) # Clean up upload on error
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred during embedding."}), 500

@app.route("/extract", methods=["POST"])
def extract():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        password = request.form.get("password", None)
        stego_type = request.form.get("type", "image") # image, audio, text
        
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)
        
        extracted_message = ""
        
        if stego_type == "image":
            # Pass password to extract_lsb, it handles decryption internally
            extracted_message = extract_lsb(upload_path, password)
        elif stego_type == "audio":
            if not filename.lower().endswith(".wav"):
                 return jsonify({"error": "Only .wav audio files are supported for extraction."}), 400
            extracted_message = extract_audio_lsb(upload_path, password)
        elif stego_type == "text":
            if not filename.lower().endswith(".txt"):
                 return jsonify({"error": "Only .txt files are supported for text extraction."}), 400
            with open(upload_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            extracted_message = extract_text(text_content, password)
        else:
            return jsonify({"error": "Invalid steganography type specified"}), 400

        # Clean up uploaded file
        # os.remove(upload_path)
        
        return jsonify({"message": extracted_message})

    except ValueError as ve:
        # os.remove(upload_path) # Clean up upload on error
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # os.remove(upload_path) # Clean up upload on error
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred during extraction."}), 500

@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    # Listen on all interfaces, important for Docker/external access
    app.run(host="0.0.0.0", port=5500, debug=True) 

