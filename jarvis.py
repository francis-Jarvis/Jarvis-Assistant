"""
Jarvis - Asistente de voz para Windows
Punto de entrada principal.

Uso: python jarvis.py
"""
import threading
from voice import hablar, escuchar
from brain import procesar
from config import ASSISTANT_NAME
from hud import HUD


def loop_de_voz(hud: HUD):
    hablar(f"{ASSISTANT_NAME} iniciado. Te escucho.")

    while True:
        hud.set_estado("escuchando")
        texto = escuchar()
        hud.set_estado("oculto")

        if not texto:
            continue  # no entendió nada, vuelve a escuchar

        respuesta = procesar(texto)

        if respuesta == "__SALIR__":
            hud.set_estado("hablando")
            hablar("Hasta luego.")
            hud.cerrar()
            return

        if respuesta:
            hud.set_estado("hablando")
            hablar(respuesta)
            hud.set_estado("oculto")


if __name__ == "__main__":
    hud = HUD()
    # El loop de voz corre en un hilo aparte; Tkinter necesita el
    # hilo principal para sí mismo (hud.iniciar(), más abajo).
    hilo = threading.Thread(target=loop_de_voz, args=(hud,), daemon=True)
    hilo.start()

    try:
        hud.iniciar()  # bloquea el hilo principal hasta que se cierre el HUD
    except KeyboardInterrupt:
        print("\n👋 Jarvis detenido.")

