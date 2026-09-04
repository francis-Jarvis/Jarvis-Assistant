# Jarvis — Asistente de voz para Windows (v1, solo comandos locales)

Versión 100% local y gratuita: escucha por micrófono y ejecuta comandos fijos.
No usa ninguna IA externa, no necesita API key ni internet (salvo para el
reconocimiento de voz de Google, que es gratis).

## 1. Instalar las dependencias

Abrí una terminal en esta carpeta y corré:

```
pip install -r requirements.txt
```

**Nota sobre PyAudio:** a veces falla instalarse directo en Windows. Si te da error, probá:

```
pip install pipwin
pipwin install pyaudio
```

## 2. Ejecutar Jarvis

```
python jarvis.py
```

Te va a saludar por voz y va a quedar escuchando. Hablále con claridad.

## Comandos que entiende

- "**qué hora es**"
- "**qué día es**"
- "**abrí [app]**" → chrome, bloc de notas, calculadora, explorador, word, excel, spotify, vscode
- "**cerrá [app]**"
- "**buscá [algo] en internet**"
- "**salí**" / "chau" → termina el programa

Si decís algo que no matchea ningún comando, Jarvis te avisa que no lo entendió
(no hay IA generativa de fondo, es todo reglas fijas).

## Cómo agregar más apps

Abrí `commands.py` y sumá entradas al diccionario `APPS`:

```python
APPS = {
    ...
    "mi_app": "nombre_del_ejecutable",
}
```

## Cómo agregar más comandos

Abrí `brain.py` y sumá un nuevo `if` dentro de `procesar()`, apuntando a una
función nueva en `commands.py`. Por ejemplo, para "subí el volumen":

1. En `commands.py`: crear función `subir_volumen()`.
2. En `brain.py`: agregar `if "subí el volumen" in texto_lower: return commands.subir_volumen()`.

## Próximos pasos (cuando esto funcione bien)

- **Wake word** ("Jarvis, ...") con Porcupine, para no tener que apretar nada.
- **Reconocimiento offline** con Vosk (no depende de internet para nada).
- **IA local gratis** con Ollama (ej. Llama 3.2 chico) para respuestas más
  flexibles, corriendo en tu propia PC sin pagar ninguna API.
- **Interfaz visual** tipo HUD con PyQt o Tkinter.

## Problemas comunes

- **No escucha nada / no reconoce**: revisá que Windows tenga permisos de
  micrófono habilitados para apps de escritorio (Configuración > Privacidad > Micrófono).
- **Error con PyAudio**: ver nota arriba, usar pipwin.
- **La voz suena en inglés**: es porque Windows no tiene una voz en español
  instalada. Andá a Configuración > Hora e idioma > Voz, y agregá una voz en español.
