"""
Plantilla de configuración de Jarvis.

Copiá este archivo como "config.py" (sin el .example) y completá tus
propias credenciales ahí. El config.py real NUNCA se sube a GitHub
(está en .gitignore) para no exponer tus API keys.
"""

# Nombre con el que Jarvis se identifica al hablar
ASSISTANT_NAME = "Jarvis"

# Palabra de activación (wake word) que hay que decir antes de cada comando
WAKE_WORD = "primo"

# Idioma para reconocimiento de voz (es-AR, es-ES, en-US, etc.)
SPEECH_LANGUAGE = "es-AR"

# Velocidad de habla (palabras por minuto aprox.)
VOICE_RATE = 175

# Credenciales de la API de Spotify (gratis, se consiguen en
# developer.spotify.com/dashboard > Create app > Settings).
SPOTIFY_CLIENT_ID = "TU_CLIENT_ID_ACA"
SPOTIFY_CLIENT_SECRET = "TU_CLIENT_SECRET_ACA"

# API key de Groq (gratis, se consigue en console.groq.com/keys)
GROQ_API_KEY = "TU_GROQ_API_KEY_ACA"
GROQ_MODEL = "llama-3.1-8b-instant"
