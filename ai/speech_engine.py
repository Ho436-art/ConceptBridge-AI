"""
ConceptBridge AI - Speech-to-Text Audio Engine
Provides direct in-browser microphone audio transcription into text.
Integrates with Google Gemini Multimodal STT and local speech recognizers.
"""

import os
import io
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> Tuple[bool, str]:
    """
    Transcribes raw audio bytes into plain English text.
    
    Args:
        audio_bytes: Raw recorded audio data from Streamlit st.audio_input.
        mime_type: MIME type of the audio stream (default 'audio/wav').
        
    Returns:
        Tuple[bool, str]: (Success, Transcribed text or error message).
    """
    if not audio_bytes or len(audio_bytes) < 800:
        return False, "Recording is empty or too short. Please speak clearly into the microphone."

    # Method 1: Try Groq Whisper (whisper-large-v3-turbo)
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key and len(groq_key) > 10:
        try:
            import urllib.request
            import uuid
            
            boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
            stt_model = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")
            
            # Construct multipart form-data payload
            body_parts = []
            # Model field
            body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{stt_model}\r\n".encode("utf-8"))
            # Language field (English default)
            body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nen\r\n".encode("utf-8"))
            # File field
            body_parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"recorded_voice.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode("utf-8")
                + audio_bytes
                + b"\r\n"
            )
            body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            payload = b"".join(body_parts)
            
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data.get("text", "").strip()
                if text:
                    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                        text = text[1:-1].strip()
                    return True, text
        except Exception:
            pass

    # Method 2: Try Google Gemini Multimodal Audio Transcription
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key and len(gemini_key) > 10:
        try:
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": mime_type if mime_type else "audio/wav",
                                    "data": b64_audio
                                }
                            },
                            {
                                "text": (
                                    "You are a speech-to-text transcriber for a learning application. "
                                    "Transcribe the spoken academic or technical question accurately into plain text. "
                                    "Return ONLY the plain transcribed words. Do NOT answer the question. Do NOT add quotes or explanations."
                                )
                            }
                        ]
                    }
                ]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                        if text:
                            # Clean surrounding quotes
                            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                                text = text[1:-1].strip()
                            return True, text
        except Exception:
            pass

    # Method 2: Try SpeechRecognition library if installed
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with io.BytesIO(audio_bytes) as audio_file:
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                if text and text.strip():
                    return True, text.strip()
    except Exception:
        pass

    return False, "Could not recognize clear speech. Please type your question or try speaking again."
