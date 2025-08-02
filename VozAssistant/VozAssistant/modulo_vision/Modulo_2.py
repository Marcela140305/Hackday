import mss
from PIL import Image
import requests
from datetime import datetime
import base64
import os

OLLAMA_MODEL = "llava:latest"  # o bakllava
OLLAMA_HOST = "http://localhost:11434/api/generate"

def capturar_pantalla(nombre_archivo="captura.png"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # pantalla principal
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(nombre_archivo)
        print(f"Captura guardada: {nombre_archivo}")
    return nombre_archivo

def convertir_imagen_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def enviar_a_llava(imagen_path, prompt="Describe esta imagen de forma concisa en español. Enfocate únicamente en el contenido del navegador que se muestra en la imagen"):
    imagen_base64 = convertir_imagen_base64(imagen_path)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [imagen_base64],
        "stream": False
    }

    try:
        res = requests.post(OLLAMA_HOST, json=payload)
        res.raise_for_status()
        data = res.json()
        descripcion = data.get("response", "").strip()
        return descripcion
    except Exception as e:
        print(f"Error al comunicar con Ollama: {e}")
        return None

def captura_y_descripcion_llava(etapa="inicio"):
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_img = f"captura_{etapa}.png"
    nombre_txt = f"captura_{etapa}.txt"

    # 1. Captura de pantalla
    capturar_pantalla(nombre_img)

    # 2. Enviar imagen a LLaVA
    descripcion = enviar_a_llava(nombre_img)
    if descripcion:
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(descripcion)
        print(f"Descripción generada guardada en: {nombre_txt}")
    else:
        print("No se generó descripción de la imagen.")

    return nombre_img, nombre_txt
