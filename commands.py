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
import win32gui
import win32con
import win32process

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


def abrir_me_gusta() -> str:
    """Abre 'Tus Me Gusta' (Liked Songs) de la cuenta de Spotify logueada."""
    try:
        os.startfile("spotify:collection:tracks")
        return "Abriendo tu lista de Tus Me Gusta en Spotify."
    except Exception as e:
        return f"No pude abrir tu lista de Tus Me Gusta: {e}"


def poner_musica(nombre_artista: str) -> str:
    nombre = nombre_artista.lower().strip()
    track_id = ARTISTAS_SPOTIFY.get(nombre)
    if not track_id:
        return f"No tengo registrado el artista '{nombre_artista}'. Podés agregarlo en commands.py."
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
