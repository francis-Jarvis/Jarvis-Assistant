# Jarvis - Asistente de voz para Windows

Asistente de voz personal en Python, con reconocimiento de voz en
español (es-AR), control de aplicaciones y del sistema, Spotify,
consulta del clima, un cerebro conversacional con IA (Groq, gratis),
y un HUD visual en pantalla estilo "arc reactor".

## Requisitos

- Windows 10/11
- Python 3.12+
- Micrófono
- Spotify instalado (para los comandos de música)

## Instalación

```
pip install -r requirements.txt
```

Copiá `config.example.py` como `config.py` y completá:
- `GROQ_API_KEY`: gratis en [console.groq.com/keys](https://console.groq.com/keys)
- `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET`: gratis en
  [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
  (creá una app, Redirect URI: `http://127.0.0.1:8888/callback`)

`config.py` nunca se sube a GitHub (está en `.gitignore`), así que tus
keys quedan solo en tu compu.

## Uso

```
python jarvis.py
```

Al arrancar, Jarvis escucha todo lo que decís (sin necesidad de decir
una palabra de activación) y va a aparecer un pequeño HUD circular en
la esquina inferior derecha de la pantalla mientras te escucha
(celeste) o mientras responde (naranja).

## Comandos disponibles

**General**
- "qué hora es"
- "qué día es"
- "salí" / "chau" (cierra Jarvis)

**Apps y ventanas**
- "abrí [app]" — ver la lista de apps soportadas en `commands.py` (APPS)
- "cerrá [app]"
- "cerrá esta ventana" (cierra la ventana activa, como Alt+F4)

**Internet y juegos**
- "buscá [algo] en internet"
- "abrí [juego de Steam]" — Pizza Tower, Balatro (agregables en `commands.py`)

**Clima**
- "qué clima hace" (usa San Juan, Argentina por defecto)
- "clima en [ciudad]" / "clima de [ciudad]"
- "va a llover"

**Spotify**
- "poné [artista o canción]" — busca automáticamente en Spotify
  cualquier canción que no esté guardada de antemano
- "poné el álbum [nombre]"
- "poné las populares de [artista]"
- "poné tus me gusta"
- "qué canción está sonando"
- "pausa" / "seguí"
- "próxima canción" / "canción anterior"

**Conversación libre**
- Cualquier otra cosa que le digas se la consulta a un modelo de IA
  gratis (Groq) y te responde de forma conversacional, con memoria de
  los últimos mensajes de la charla.

## Agregar más apps, artistas o juegos

Todo está en `commands.py`, en diccionarios simples (`APPS`,
`ARTISTAS_SPOTIFY`, `ALBUMES_SPOTIFY`, `JUEGOS_STEAM`,
`POPULARES_POR_ARTISTA`). Sumar uno nuevo es agregar una línea al
diccionario correspondiente; hay comentarios explicando cómo conseguir
cada ID.

## Generar el .exe (arranque automático)

```
pyinstaller --onefile --noconsole --name Jarvis jarvis.py
```

El ejecutable queda en `dist/Jarvis.exe`. Para que arranque solo con
Windows, poné un acceso directo a ese `.exe` en la carpeta de inicio
(`Win + R` → `shell:startup`).

> Nota: Windows Defender puede marcar el `.exe` como sospechoso
> (`Trojan:Win32/Wacatac.B!ml`). Es un **falso positivo conocido** de
> los ejecutables generados con PyInstaller `--onefile` (por cómo se
> autoextraen en memoria al abrirse), no significa que el código tenga
> nada malicioso — podés revisarlo vos mismo, es el mismo código de
> este repo.

## Estructura del proyecto

- `jarvis.py` — punto de entrada, arranca el HUD y el loop de voz
- `voice.py` — reconocimiento de voz (Google STT) y síntesis (pyttsx3)
- `brain.py` — interpreta el texto y decide qué comando ejecutar (o
  consulta a Groq si no matchea ninguno)
- `commands.py` — todas las acciones concretas (abrir apps, Spotify,
  clima, etc.)
- `hud.py` — la ventana flotante animada
- `config.py` — tus credenciales (no se sube a git)
- `config.example.py` — plantilla de config sin credenciales

## Problemas comunes

- **No escucha nada / no reconoce**: revisá que Windows tenga permisos
  de micrófono habilitados para apps de escritorio (Configuración >
  Privacidad > Micrófono).
- **Error con PyAudio**: si falla la instalación, probá `pip install
  pipwin` y después `pipwin install pyaudio`.
- **La voz suena en inglés**: Windows no tiene una voz en español
  instalada. Andá a Configuración > Hora e idioma > Voz, y agregá una
  voz en español.
- **Antivirus marca el .exe como troyano**: ver la nota en la sección
  de "Generar el .exe" más arriba — es un falso positivo conocido.

## Ideas para más adelante

- Wake word (decir "Jarvis" antes de cada comando) con algo tipo Porcupine
- Reconocimiento de voz offline con Vosk, sin depender de internet
- IA local y gratis con Ollama, corriendo en la propia PC
