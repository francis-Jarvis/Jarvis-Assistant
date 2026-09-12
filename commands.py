"""
Comandos que Jarvis puede ejecutar directamente en Windows,
sin necesidad de consultar a la IA.
Cada función devuelve el texto que Jarvis debe decir en voz alta.
"""
import subprocess
import webbrowser
import datetime
import os
import threading
import time
import requests
import win32gui
import win32con
import win32process
import win32api
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Mapeo de nombres comunes a comandos/ejecutables de Windows.
# Sumá acá las apps que más uses.
#
# OJO: algunas apps (Discord, WhatsApp, Telegram, Steam, Epic Games) no
# quedan en el PATH de Windows por defecto al instalarse. Si alguna no abre,
# hay que reemplazar el valor por la ruta completa al .exe, algo como:
# "discord": r"C:\Users\TU_USUARIO\AppData\Local\Discord\Update.exe --processStart Discord.exe"
APPS = {
    # Navegadores
    "chrome": "chrome",
    "navegador": "chrome",
    "firefox": "firefox",
    "edge": "msedge",

    # Utilidades de Windows
    "bloc de notas": "notepad",
    "notepad": "notepad",
    "calculadora": "calc",
    "explorador de archivos": "explorer",
    "explorador": "explorer",
    "panel de control": "control",
    "configuración": "ms-settings:",

    # Ofimática / trabajo
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "teams": "ms-teams",
    "zoom": "zoom",
    "vscode": "code",
    "visual studio code": "code",

    # Multimedia
    "spotify": "spotify",
    "vlc": "vlc",

    # Comunicación
    "discord": "discord",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",

    # Gaming
    "steam": "steam",
    "epic games": "EpicGamesLauncher",
}


# Juegos de Steam: se abren con el protocolo steam://rungameid/<ID>,
# así Steam los busca solo sin importar en qué carpeta estén instalados.
# Para agregar un juego nuevo: buscá su "app id" en steamdb.info
JUEGOS_STEAM = {
    "pizza tower": "2231450",
    "balatro": "2379780",
}


# Artistas de Spotify: se abren con el protocolo spotify:artist:<ID>,
# que abre Spotify directo en la página del artista (reproduciendo su top).
# Para agregar un artista nuevo: buscalo en open.spotify.com y copiá el
# código que aparece después de "/artist/" en la URL.
# Artistas de Spotify: se abren con el protocolo spotify:track:<ID> de su
# canción más popular, porque el URI de "artist" solo abre la página sin
# reproducir, mientras que el de "track" sí dispara el play automático.
# Para agregar un artista nuevo: buscá su canción más popular en
# kworb.net/spotify/artist/<ID_del_artista>_songs.html y copiá el ID
# del track (lo que sigue a "/track/" en el link de esa canción).
ARTISTAS_SPOTIFY = {
    "la mosca": "19CmuECYssqkPWANF4nLWM",  # "Para No Verte Más", su canción más escuchada
}


# Álbumes de Spotify: se abren con el protocolo spotify:album:<ID>, que
# sí dispara la reproducción automática (a diferencia del URI de artista).
# Para agregar un álbum nuevo: buscalo en open.spotify.com y copiá el
# código que aparece después de "/album/" en la URL.
ALBUMES_SPOTIFY = {
    "vísperas de carnaval": "4vIw5XspQuPt04VHX5oK5W",
    "visperas de carnaval": "4vIw5XspQuPt04VHX5oK5W",
}


def poner_album(nombre_album: str) -> str:
    nombre = nombre_album.lower().strip()
    album_id = ALBUMES_SPOTIFY.get(nombre)
    if not album_id:
        return f"No tengo registrado el álbum '{nombre_album}'. Podés agregarlo en commands.py."
    try:
        os.startfile(f"spotify:album:{album_id}")
        return f"Poniendo el álbum {nombre_album}."
    except Exception as e:
        return f"No pude abrir el álbum {nombre_album}: {e}"


# Canciones más escuchadas de La Mosca según Spotify (mismo orden que
# aparece en "Populares" en su perfil), con la duración aproximada de
# cada una en segundos, para poder encadenarlas una detrás de otra.
# Fuente de los IDs y el orden: kworb.net/spotify/artist (streams totales).
POPULARES_LA_MOSCA = [
    ("19CmuECYssqkPWANF4nLWM", 191),  # Para No Verte Más
    ("71ZEPoxREWtwIlevFzz2dB", 204),  # Te Quiero Comer La Boca
    ("2BCaOXnLPGrFS3moTJxnAq", 227),  # Todos Tenemos Un Amor
    ("5r1ZxyU8So2hMac9qd7v3A", 141),  # Muchachos, Ahora Nos Volvimos a Ilusionar
    ("2vwJC3c69M9B8WJpVUoKix", 205),  # Baila Para Mi
    ("333fEkaKfD2EO9P1FSV9WT", 210),  # Muchachos Esta Noche Me Emborracho
    ("6OIC1huIZ1u93ymLNR4got", 210),  # Yo Te Quiero Dar
    ("74Afq4nheLYs6FIob8tWLQ", 210),  # El Demonio (Está En Esa Mujer)
]

# Mismo esquema, pero por artista, para poder sumar otros más adelante.
POPULARES_POR_ARTISTA = {
    "la mosca": POPULARES_LA_MOSCA,
}


def _reproducir_cola(canciones: list[tuple[str, int]]):
    """Corre en un hilo aparte: va reproduciendo temas uno detrás de otro."""
    for track_id, duracion_seg in canciones:
        try:
            os.startfile(f"spotify:track:{track_id}")
        except Exception:
            pass  # si falla una canción puntual, sigue con la próxima
        time.sleep(duracion_seg)


def reproducir_populares(nombre_artista: str) -> str:
    nombre = nombre_artista.lower().strip()
    canciones = POPULARES_POR_ARTISTA.get(nombre)
    if not canciones:
        return f"No tengo la lista de populares de '{nombre_artista}'. Podés agregarla en commands.py."

    hilo = threading.Thread(target=_reproducir_cola, args=(canciones,), daemon=True)
    hilo.start()
    return (
        f"Poniendo las canciones más escuchadas de {nombre_artista}, "
        f"{len(canciones)} temas en fila, empezando ahora."
    )


# Códigos de las teclas multimedia (funcionan con Spotify, YouTube,
# o cualquier reproductor que esté activo, no solo Spotify).
_VK_MEDIA_NEXT_TRACK = 0xB0
_VK_MEDIA_PREV_TRACK = 0xB1
_VK_MEDIA_PLAY_PAUSE = 0xB3


def _presionar_tecla_multimedia(codigo: int):
    win32api.keybd_event(codigo, 0, 0, 0)  # presionar
    time.sleep(0.05)
    win32api.keybd_event(codigo, 0, win32con.KEYEVENTF_KEYUP, 0)  # soltar


def pausar_reanudar_musica() -> str:
    try:
        _presionar_tecla_multimedia(_VK_MEDIA_PLAY_PAUSE)
        return "Listo."
    except Exception as e:
        return f"No pude pausar/reanudar la música: {e}"


def siguiente_cancion() -> str:
    try:
        _presionar_tecla_multimedia(_VK_MEDIA_NEXT_TRACK)
        return "Pasando a la siguiente canción."
    except Exception as e:
        return f"No pude pasar de canción: {e}"


def cancion_anterior() -> str:
    try:
        _presionar_tecla_multimedia(_VK_MEDIA_PREV_TRACK)
        return "Volviendo a la canción anterior."
    except Exception as e:
        return f"No pude volver de canción: {e}"


def obtener_cancion_actual() -> str:
    """
    Lee qué se está reproduciendo en Spotify a partir del título de su
    ventana (en Windows, Spotify muestra 'Artista - Canción' en el título
    de su ventana mientras algo está sonando).
    """
    titulo_encontrado = []

    def _revisar_ventana(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            import psutil
            proceso = psutil.Process(pid)
            if proceso.name().lower() == "spotify.exe":
                titulo = win32gui.GetWindowText(hwnd)
                if titulo:
                    titulo_encontrado.append(titulo)
        except Exception:
            pass

    win32gui.EnumWindows(_revisar_ventana, None)

    if not titulo_encontrado:
        return "No encontré Spotify abierto en este momento."

    # Spotify suele tener varias ventanas; nos quedamos con la más larga
    # (la ventana principal con el título real, no una vacía tipo "Spotify")
    titulo = max(titulo_encontrado, key=len).strip()
    titulo_lower = titulo.lower()

    # Casos especiales: nada sonando, o publicidad (cuenta gratis)
    if titulo_lower in ("spotify", "spotify free", "spotify premium"):
        return "Spotify está abierto, pero no parece estar reproduciendo nada ahora mismo."

    if "advertisement" in titulo_lower or "publicidad" in titulo_lower:
        return "Ahora mismo está sonando una publicidad en Spotify."

    # El formato habitual es "Artista - Canción": lo separamos para que
    # suene más natural al decirlo en voz alta, en vez de leerlo tal cual.
    if " - " in titulo:
        artista, cancion = titulo.split(" - ", 1)
        return f"Está sonando {cancion.strip()}, de {artista.strip()}."

    return f"Ahora está sonando: {titulo}."


def abrir_me_gusta() -> str:
    """Abre 'Tus Me Gusta' (Liked Songs) de la cuenta de Spotify logueada."""
    try:
        os.startfile("spotify:collection:tracks")
        return "Abriendo tu lista de Tus Me Gusta en Spotify."
    except Exception as e:
        return f"No pude abrir tu lista de Tus Me Gusta: {e}"


_token_spotify = {"valor": None, "expira": 0}


def _obtener_token_spotify() -> str | None:
    """
    Consigue (o reutiliza si todavía es válido) un token de acceso a la
    API de Spotify usando las credenciales de la app (Client Credentials
    Flow). Este tipo de token solo sirve para BUSCAR, no para controlar
    la reproducción de tu cuenta directamente (para eso usamos los
    protocolos spotify:track:... como ya veníamos haciendo).
    """
    ahora = time.time()
    if _token_spotify["valor"] and ahora < _token_spotify["expira"]:
        return _token_spotify["valor"]

    if SPOTIFY_CLIENT_ID == "TU_CLIENT_ID_ACA":
        return None  # todavía no configuraste las credenciales

    try:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
            timeout=10,
        )
        resp.raise_for_status()
        datos = resp.json()
        _token_spotify["valor"] = datos["access_token"]
        _token_spotify["expira"] = ahora + datos.get("expires_in", 3600) - 60
        return _token_spotify["valor"]
    except Exception:
        return None


def buscar_y_reproducir_cancion(consulta: str) -> str:
    """
    Busca cualquier canción por nombre (y opcionalmente artista) usando
    la API de Spotify, y reproduce el primer resultado.
    """
    token = _obtener_token_spotify()
    if not token:
        return (
            "No tengo configuradas las credenciales de la API de Spotify. "
            "Agregalas en config.py para poder buscar cualquier canción."
        )

    try:
        resp = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": consulta, "type": "track", "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("tracks", {}).get("items", [])

        if not items:
            return f"No encontré ninguna canción llamada '{consulta}'."

        track = items[0]
        track_id = track["id"]
        nombre_cancion = track["name"]
        artistas = ", ".join(a["name"] for a in track["artists"])

        os.startfile(f"spotify:track:{track_id}")
        return f"Poniendo {nombre_cancion}, de {artistas}."
    except Exception as e:
        return f"Tuve un problema buscando esa canción: {e}"


def poner_musica(nombre_artista: str) -> str:
    nombre = nombre_artista.lower().strip()

    # Coincidencia flexible: si lo que pediste CONTIENE (o coincide
    # exacto con) alguno de los artistas ya guardados, usamos ese —
    # así "poné la mosca por favor" también encuentra a "la mosca".
    track_id = ARTISTAS_SPOTIFY.get(nombre)
    artista_encontrado = nombre
    if not track_id:
        for clave in ARTISTAS_SPOTIFY:
            if clave in nombre:
                track_id = ARTISTAS_SPOTIFY[clave]
                artista_encontrado = clave
                break

    if not track_id:
        # No está en nuestra lista fija: buscamos dinámicamente por la API.
        return buscar_y_reproducir_cancion(nombre_artista)

    nombre_artista = artista_encontrado
    try:
        os.startfile(f"spotify:track:{track_id}")
        return (
            f"Poniendo {nombre_artista}, empezando por su canción más escuchada. "
            "Si tenés el Autoplay de Spotify activado, cuando termine va a seguir "
            "solo con más temas del mismo estilo o del mismo artista."
        )
    except Exception as e:
        return f"No pude abrir {nombre_artista}: {e}"


def abrir_app(nombre_app: str) -> str:
    nombre = nombre_app.lower().strip()

    # Primero revisa si es un juego de Steam
    steam_id = JUEGOS_STEAM.get(nombre)
    if steam_id:
        try:
            os.startfile(f"steam://rungameid/{steam_id}")
            return f"Abriendo {nombre_app} en Steam."
        except Exception as e:
            return f"No pude abrir {nombre_app}: {e}"

    ejecutable = APPS.get(nombre)
    if not ejecutable:
        return f"No tengo registrada la app '{nombre_app}'. Podés agregarla en commands.py."
    try:
        subprocess.Popen(ejecutable, shell=True)
        return f"Abriendo {nombre_app}."
    except Exception as e:
        return f"No pude abrir {nombre_app}: {e}"


def decir_hora() -> str:
    ahora = datetime.datetime.now().strftime("%H:%M")
    return f"Son las {ahora}."


def decir_fecha() -> str:
    hoy = datetime.datetime.now().strftime("%d/%m/%Y")
    return f"Hoy es {hoy}."


def buscar_en_internet(consulta: str) -> str:
    url = f"https://www.google.com/search?q={consulta.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Buscando '{consulta}' en internet."


# Traducción de los "weather codes" que usa Open-Meteo (estándar WMO)
# a una descripción corta en español.
_CODIGOS_CLIMA = {
    0: "cielo despejado",
    1: "mayormente despejado",
    2: "parcialmente nublado",
    3: "nublado",
    45: "con neblina",
    48: "con neblina y escarcha",
    51: "con llovizna leve",
    53: "con llovizna moderada",
    55: "con llovizna intensa",
    61: "con lluvia leve",
    63: "con lluvia moderada",
    65: "con lluvia fuerte",
    71: "con nevadas leves",
    73: "con nevadas moderadas",
    75: "con nevadas fuertes",
    80: "con chaparrones leves",
    81: "con chaparrones moderados",
    82: "con chaparrones fuertes",
    95: "con tormenta eléctrica",
    96: "con tormenta eléctrica y granizo",
    99: "con tormenta eléctrica y granizo fuerte",
}


def obtener_clima(ciudad: str = "") -> str:
    """
    Consulta el clima actual (y si va a llover en las próximas horas)
    usando Open-Meteo, una API meteorológica gratuita y sin necesidad
    de API key. Si no se especifica ciudad, usa San Juan, Argentina.
    """
    ciudad = ciudad.strip() or "San Juan, Argentina"

    try:
        # Paso 1: convertir el nombre de la ciudad en coordenadas
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es"},
            timeout=10,
        )
        geo.raise_for_status()
        resultados = geo.json().get("results")
        if not resultados:
            return f"No encontré la ciudad '{ciudad}'."

        lugar = resultados[0]
        lat, lon = lugar["latitude"], lugar["longitude"]
        nombre_lugar = lugar.get("name", ciudad)

        # Paso 2: pedir el clima actual + probabilidad de lluvia próxima
        clima = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,weather_code",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=10,
        )
        clima.raise_for_status()
        datos = clima.json()

        actual = datos["current"]
        temperatura = round(actual["temperature_2m"])
        sensacion = round(actual["apparent_temperature"])
        descripcion = _CODIGOS_CLIMA.get(actual["weather_code"], "condiciones variables")

        # Probabilidad de lluvia más alta en las próximas 6 horas
        probs_lluvia = datos.get("hourly", {}).get("precipitation_probability", [])
        prob_maxima = max(probs_lluvia[:6]) if probs_lluvia else None

        respuesta = f"En {nombre_lugar} hay {temperatura} grados, {descripcion}"
        if sensacion != temperatura:
            respuesta += f", sensación térmica de {sensacion} grados"
        respuesta += "."

        if prob_maxima is not None:
            if prob_maxima >= 50:
                respuesta += f" Hay {prob_maxima}% de probabilidad de lluvia en las próximas horas, llevá paraguas."
            elif prob_maxima >= 20:
                respuesta += f" Hay una probabilidad baja de lluvia, {prob_maxima}%."

        return respuesta
    except Exception as e:
        return f"No pude consultar el clima: {e}"


def apagar_pc() -> str:
    # Comentado por seguridad. Descomentar si realmente lo querés habilitar.
    # os.system("shutdown /s /t 30")
    return "Por seguridad, el apagado automático está desactivado en el código. Podés habilitarlo en commands.py."


def cerrar_app(nombre_app: str) -> str:
    nombre = nombre_app.lower().strip()
    ejecutable = APPS.get(nombre, nombre)
    try:
        subprocess.run(["taskkill", "/f", "/im", f"{ejecutable}.exe"], capture_output=True)
        return f"Cerrando {nombre_app}."
    except Exception as e:
        return f"No pude cerrar {nombre_app}: {e}"


def cerrar_ventana_activa() -> str:
    """Cierra la ventana que está actualmente en foco (como Alt+F4)."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return "No encontré ninguna ventana activa para cerrar."

        titulo = win32gui.GetWindowText(hwnd) or "la ventana activa"

        # No cerrar el escritorio ni la propia terminal de Jarvis por error
        clase = win32gui.GetClassName(hwnd)
        if clase in ("Progman", "WorkerW"):
            return "Esa es el escritorio, no hay nada que cerrar ahí."

        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return f"Cerrando {titulo}."
    except Exception as e:
        return f"No pude cerrar la ventana activa: {e}"
