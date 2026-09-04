"""
Módulo de voz: escuchar (Speech-to-Text) y hablar (Text-to-Speech).
"""
import speech_recognition as sr
import pyttsx3
from config import SPEECH_LANGUAGE, VOICE_RATE

# --- Configuración del motor de voz (offline, usa las voces de Windows) ---
engine = pyttsx3.init()
engine.setProperty("rate", VOICE_RATE)

# Intenta usar una voz en español si está disponible en el sistema
for voice in engine.getProperty("voices"):
    if "spanish" in voice.name.lower() or "español" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break


def hablar(texto: str):
    """Hace que Jarvis diga el texto en voz alta."""
    print(f"🤖 Jarvis: {texto}")
    engine.say(texto)
    engine.runAndWait()


def escuchar(timeout: int = 5, phrase_time_limit: int = 8) -> str:
    """
    Escucha por el micrófono y devuelve el texto reconocido.
    Devuelve una cadena vacía si no entendió o hubo timeout.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️  Escuchando...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""

    try:
        texto = recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
        print(f"🗣️  Vos: {texto}")
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"⚠️  Error con el servicio de reconocimiento: {e}")
        return ""
