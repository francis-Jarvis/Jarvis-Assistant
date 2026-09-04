"""
El "cerebro" de Jarvis: interpreta el texto reconocido por voz
y lo matchea contra los comandos conocidos. 100% local, sin IA externa.
"""
import re
import commands


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

    # Ningún comando conocido matcheó
    return "No entendí ese comando. Decime 'qué hora es', 'abrí' alguna app, o 'buscá algo en internet'."
