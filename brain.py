"""
El "cerebro" de Jarvis: interpreta el texto reconocido por voz y lo
matchea contra los comandos conocidos. Si no matchea ninguno, se lo
consulta a un modelo de IA gratis (Groq) para una respuesta conversacional.
"""
import re
import requests
import commands
from config import GROQ_API_KEY, GROQ_MODEL

# Historial simple de la conversación (para que Jarvis tenga contexto
# de lo último que hablaron, no cada vez arranca de cero)
historial = []
MAX_HISTORIAL = 10


def consultar_ia(texto: str) -> str:
    if GROQ_API_KEY == "TU_GROQ_API_KEY_ACA":
        return "No entendí ese comando, y todavía no configuraste la API key de Groq para charlar de otras cosas."

    historial.append({"role": "user", "content": texto})

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": GROQ_MODEL,
                "max_tokens": 500,
                "reasoning_effort": "low",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Sos Jarvis, un asistente de voz para Windows. "
                            "Respondé siempre en español rioplatense, de forma breve "
                            "y directa (1 a 3 oraciones), porque tu respuesta se va a "
                            "leer en voz alta. No uses markdown, listas ni emojis."
                        ),
                    },
                    *historial[-MAX_HISTORIAL:],
                ],
            },
            timeout=15,
        )
        resp.raise_for_status()
        texto_respuesta = resp.json()["choices"][0]["message"]["content"]
        historial.append({"role": "assistant", "content": texto_respuesta})
        return texto_respuesta
    except Exception as e:
        return f"Tuve un problema para conectarme con la IA: {e}"


def procesar(texto: str) -> str:
    """
    Recibe el texto reconocido por voz y devuelve la respuesta hablada.
    """
    texto_lower = texto.lower().strip()

    if not texto_lower:
        return ""

    if "qué hora es" in texto_lower or "que hora es" in texto_lower:
        return commands.decir_hora()

    if "qué día es" in texto_lower or "que dia es" in texto_lower or "qué fecha es" in texto_lower:
        return commands.decir_fecha()

    if texto_lower in ("pausa", "pausá", "poné en pausa", "pausá la música", "pausá la canción"):
        return commands.pausar_reanudar_musica()

    if texto_lower in ("seguí", "segui", "reanudá", "reanuda", "dale play", "play"):
        return commands.pausar_reanudar_musica()

    if "próxima canción" in texto_lower or "proxima cancion" in texto_lower or \
            "siguiente canción" in texto_lower or "siguiente cancion" in texto_lower or \
            "siguiente tema" in texto_lower or "próximo tema" in texto_lower:
        return commands.siguiente_cancion()

    if "canción anterior" in texto_lower or "cancion anterior" in texto_lower or \
            "tema anterior" in texto_lower or "anterior canción" in texto_lower:
        return commands.cancion_anterior()

    if "qué canción" in texto_lower or "que cancion" in texto_lower or \
            "qué está sonando" in texto_lower or "que esta sonando" in texto_lower or \
            "qué se está reproduciendo" in texto_lower or "que se esta reproduciendo" in texto_lower:
        return commands.obtener_cancion_actual()

    if "tus me gusta" in texto_lower or "mis me gusta" in texto_lower or "canciones que me gustan" in texto_lower:
        return commands.abrir_me_gusta()

    match_album = re.search(r"pon[eé] (?:el )?[aá]lbum (?:de )?(.+)", texto_lower)
    if match_album:
        return commands.poner_album(match_album.group(1))

    match_populares = re.search(r"pon[eé] (?:las )?(?:m[aá]s escuchadas|populares|canciones populares)(?: de)? (.+)", texto_lower)
    if match_populares:
        return commands.reproducir_populares(match_populares.group(1))

    match_musica = re.search(r"pon[eé] (?:música de |m[uú]sica de )?(.+)", texto_lower)
    if match_musica:
        return commands.poner_musica(match_musica.group(1))

    if "qué clima" in texto_lower or "que clima" in texto_lower or \
            "cómo está el clima" in texto_lower or "como esta el clima" in texto_lower or \
            "va a llover" in texto_lower or "qué tiempo hace" in texto_lower or \
            "que tiempo hace" in texto_lower or texto_lower.startswith("clima") or \
            "poné el clima" in texto_lower or "pone el clima" in texto_lower:
        match_ciudad = re.search(r"(?:clima|tiempo) (?:en|de) (.+)", texto_lower)
        ciudad = match_ciudad.group(1) if match_ciudad else ""
        return commands.obtener_clima(ciudad)

    match_abrir = re.search(r"abr[ií] (.+)", texto_lower)
    if match_abrir:
        return commands.abrir_app(match_abrir.group(1))

    if "cerrá esta ventana" in texto_lower or "cerra esta ventana" in texto_lower \
            or "cerrá la ventana" in texto_lower or "cerra la ventana" in texto_lower \
            or "cerrá ventana activa" in texto_lower or "cerra ventana activa" in texto_lower:
        return commands.cerrar_ventana_activa()

    match_cerrar = re.search(r"cerr[áa] (.+)", texto_lower)
    if match_cerrar:
        return commands.cerrar_app(match_cerrar.group(1))

    match_buscar = re.search(r"busc[áa] (.+) en internet", texto_lower)
    if match_buscar:
        return commands.buscar_en_internet(match_buscar.group(1))

    if "apagate" in texto_lower or "apagá la pc" in texto_lower or "apaga la pc" in texto_lower:
        return commands.apagar_pc()

    if texto_lower in ("salí", "sali", "chau", "adiós", "adios", "terminá", "termina"):
        return "__SALIR__"

    # Ningún comando conocido matcheó: le preguntamos a la IA
    return consultar_ia(texto)
