"""
Jarvis - Asistente de voz para Windows
Punto de entrada principal.

Uso: python jarvis.py
"""
from voice import hablar, escuchar
from brain import procesar
from config import ASSISTANT_NAME


def main():
    hablar(f"{ASSISTANT_NAME} iniciado. Te escucho.")

    while True:
        texto = escuchar()

        if not texto:
            continue  # no entendió nada, vuelve a escuchar

        respuesta = procesar(texto)

        if respuesta == "__SALIR__":
            hablar("Hasta luego.")
            break

        if respuesta:
            hablar(respuesta)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Jarvis detenido.")
