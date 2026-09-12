"""
HUD visual de Jarvis: una ventanita flotante estilo "arc reactor" de
Iron Man, que aparece en una esquina de la pantalla solo mientras
Jarvis está escuchando o hablando, y se esconde el resto del tiempo.

Corre en el hilo principal (requisito de Tkinter en Windows), mientras
el resto de Jarvis (escuchar/procesar/hablar) corre en un hilo aparte
y le avisa qué mostrar a través de una cola thread-safe.
"""
import tkinter as tk
import queue
import math

TAMANIO = 220  # ancho/alto de la ventana, en píxeles
COLOR_FONDO = "#010203"  # casi negro, se usa como "transparente"

# Colores por estado
COLOR_IDLE = "#0a3d4a"
COLOR_ESCUCHANDO = "#00e5ff"
COLOR_HABLANDO = "#ffb300"


class HUD:
    def __init__(self):
        self._cola: queue.Queue[str] = queue.Queue()
        self._estado = "oculto"  # oculto | escuchando | hablando
        self._angulo = 0
        self._root = None

    # --- API pública, llamada desde el hilo de voz ---
    def set_estado(self, estado: str):
        self._cola.put(estado)

    def cerrar(self):
        self._cola.put("__CERRAR__")

    # --- Todo lo de abajo corre en el hilo principal (Tkinter) ---
    def iniciar(self):
        self._root = tk.Tk()
        self._root.overrideredirect(True)  # sin bordes ni barra de título
        self._root.attributes("-topmost", True)  # siempre visible arriba de todo
        self._root.attributes("-transparentcolor", COLOR_FONDO)  # fondo "invisible"
        self._root.config(bg=COLOR_FONDO)

        # Posición: abajo a la derecha, con un margen
        ancho_pantalla = self._root.winfo_screenwidth()
        alto_pantalla = self._root.winfo_screenheight()
        x = ancho_pantalla - TAMANIO - 30
        y = alto_pantalla - TAMANIO - 80
        self._root.geometry(f"{TAMANIO}x{TAMANIO}+{x}+{y}")

        self._canvas = tk.Canvas(
            self._root, width=TAMANIO, height=TAMANIO,
            bg=COLOR_FONDO, highlightthickness=0,
        )
        self._canvas.pack()

        self._root.withdraw()  # arranca escondida
        self._procesar_cola()
        self._animar()
        self._root.mainloop()

    def _procesar_cola(self):
        try:
            while True:
                estado = self._cola.get_nowait()
                if estado == "__CERRAR__":
                    self._root.destroy()
                    return
                self._estado = estado
                if estado == "oculto":
                    self._root.withdraw()
                else:
                    self._root.deiconify()
        except queue.Empty:
            pass
        self._root.after(50, self._procesar_cola)

    def _animar(self):
        if self._estado != "oculto":
            self._dibujar()
        self._angulo = (self._angulo + 6) % 360
        self._root.after(40, self._animar)

    def _dibujar(self):
        c = self._canvas
        c.delete("all")
        cx = cy = TAMANIO / 2
        color = COLOR_ESCUCHANDO if self._estado == "escuchando" else COLOR_HABLANDO

        # Anillo exterior fijo, tenue
        c.create_oval(15, 15, TAMANIO - 15, TAMANIO - 15, outline=COLOR_IDLE, width=2)

        # Anillo medio, con marcas tipo "radar"
        for i in range(24):
            a = math.radians(i * 15)
            r1, r2 = 30, 38
            x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a)
            x2, y2 = cx + r2 * math.cos(a), cy + r2 * math.sin(a)
            c.create_line(x1, y1, x2, y2, fill=COLOR_IDLE, width=1)

        # Arco animado girando (el "pulso" de actividad)
        c.create_arc(
            25, 25, TAMANIO - 25, TAMANIO - 25,
            start=self._angulo, extent=70,
            outline=color, width=4, style="arc",
        )
        c.create_arc(
            25, 25, TAMANIO - 25, TAMANIO - 25,
            start=self._angulo + 180, extent=70,
            outline=color, width=4, style="arc",
        )

        # Círculo interior con brillo pulsante (varía según el ángulo)
        pulso = 3 + 2 * abs(math.sin(math.radians(self._angulo * 2)))
        c.create_oval(
            cx - 45, cy - 45, cx + 45, cy + 45,
            outline=color, width=pulso,
        )

        # Texto central
        c.create_text(
            cx, cy, text="JARVIS", fill=color,
            font=("Consolas", 13, "bold"),
        )
