import pyttsx3
import os

def leer_respuesta_y_hablar(path_respuesta="respuesta.txt"):
    if not os.path.exists(path_respuesta):
        print("No se encontró el archivo de respuesta.")
        return

    with open(path_respuesta, "r", encoding="utf-8") as f:
        texto = f.read().strip()

    if not texto:
        print("El archivo de respuesta está vacío.")
        return

    print(f"\nLEYENDO RESPUESTA:\n{texto}\n")

    engine = pyttsx3.init()
    engine.setProperty('voice', 'spanish-latin-am')

    engine.say(texto)
    engine.runAndWait()
