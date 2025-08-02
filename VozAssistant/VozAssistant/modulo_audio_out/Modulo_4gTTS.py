from gtts import gTTS
from playsound import playsound
import os

def leer_respuesta_y_hablar(path_respuesta="respuesta.txt", ruta_audio="NoAyudar.mp3"):
    if not os.path.exists(path_respuesta):
        print("No se encontró el archivo de respuesta.")
        return

    with open(path_respuesta, "r", encoding="utf-8") as f:
        texto = f.read().strip()

    if not texto:
        print("El archivo de respuesta está vacío.")
        return

    print(f"\nLEYENDO RESPUESTA:\n{texto}\n")

    # Eliminar audio anterior si existe
    if os.path.exists(ruta_audio):
        try:
            os.remove(ruta_audio)
        except Exception as e:
            print(f"No se pudo eliminar el audio anterior: {e}")
            return

    try:
        # Generar nueva voz
        tts = gTTS(text="Entendido, no realizaré ninguna acción por ahora.", lang='es')
        tts.save(ruta_audio)

        # Reproducir voz
        playsound(ruta_audio)
    except Exception as e:
        print(f"Error en generación o reproducción de audio: {e}")