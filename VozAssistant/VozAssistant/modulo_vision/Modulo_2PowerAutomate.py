import mss
from PIL import Image
import base64
import requests
from datetime import datetime
import os

# URL del flujo de Power Automate
POWER_AUTOMATE_URL = "https://prod-19.northeurope.logic.azure.com:443/workflows/81ce8ecf45104920af138ee6a9a84442/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=2P6oOx-aMoDC1czFFV6NWVgh3vUtHhmWja3LJf2SLhY" 

def capturar_pantalla(nombre_archivo="captura.png"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(nombre_archivo)
        print(f"Captura guardada: {nombre_archivo}")
    return nombre_archivo

def convertir_imagen_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def enviar_a_power_automate(imagen_base64):
    payload = {
        "imagen": imagen_base64  # entrada en base 64
    }

    try:
        res = requests.post(POWER_AUTOMATE_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        descripcion = data.get("descripcion", "").strip()  # respuesta JSON
        return descripcion
    except Exception as e:
        print(f"Error al comunicar con Power Automate: {e}")
        return None

def captura_y_descripcion_llava(etapa="inicio"):
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_img = f"captura_{etapa}.png"
    nombre_txt = f"captura_{etapa}.txt"

    capturar_pantalla(nombre_img)
    imagen_base64 = convertir_imagen_base64(nombre_img)
    descripcion = enviar_a_power_automate(imagen_base64)

    if descripcion:
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(descripcion)
        print(f"Descripción guardada en: {nombre_txt}")
    else:
        print("No se obtuvo descripción de Power Automate.")

    return nombre_img, nombre_txt