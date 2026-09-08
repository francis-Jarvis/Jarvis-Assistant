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

# --- Configuración del reconocimiento de voz ---
# Se crea UNA sola vez (no en cada escucha) para que la calibración de
# ruido ambiente se mantenga estable entre una escucha y la siguiente.
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True  # se auto-ajusta con el tiempo
recognizer.pause_threshold = 0.8  # cuánto silencio espera antes de cortar la frase

_calibrado = False  # para calibrar el ruido ambiente una sola vez, al inicio

# Frases reconocidas más cortas que esto se descartan como ruido/error
# (evita que un sonido suelto se interprete como una palabra random)
LARGO_MINIMO_TEXTO = 3


def hablar(texto: str):
    """Hace que Jarvis diga el texto en voz alta."""
    print(f"🤖 Jarvis: {texto}")
    engine.say(texto)
    engine.runAndWait()


def escuchar(timeout: int = 5, phrase_time_limit: int = 8) -> str:
    """
    Escucha por el micrófono y devuelve el texto reconocido.
    Devuelve una cadena vacía si no entendió, hubo timeout, o el
    resultado es demasiado corto para ser un comando real.
    """
    global _calibrado

    with sr.Microphone() as source:
        if not _calibrado:
            print("🎚️  Calibrando ruido ambiente (un momento)...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            _calibrado = True

        print("🎙️  Escuchando...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""

    try:
        texto = recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)

        if len(texto.strip()) < LARGO_MINIMO_TEXTO:
            return ""  # descartado: muy corto, probablemente ruido

        print(f"🗣️  Vos: {texto}")
        return texto
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"⚠️  Error con el servicio de reconocimiento: {e}")
        return ""


def recalibrar_ruido():
    """
    Fuerza una nueva calibración de ruido ambiente en la próxima escucha.
    Útil si cambiaste de lugar o el ambiente se puso más ruidoso/silencioso.
    """
    global _calibrado
    _calibrado = False
