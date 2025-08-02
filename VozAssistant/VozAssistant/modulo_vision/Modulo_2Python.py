from PIL import Image
import pytesseract
import os
import mss
import requests
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def capturar_pantalla(nombre_archivo="captura.png"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # pantalla principal
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(nombre_archivo)
        print(f"Captura guardada: {nombre_archivo}")
    return nombre_archivo


def extraer_texto(img_path):
    img = Image.open(img_path)
    texto_extraido = pytesseract.image_to_string(img, lang="eng") 
    return texto_extraido


def captura_y_descripcion_llava(etapa="inicio"):
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_img = f"captura_{etapa}.png"
    nombre_txt = f"captura_{etapa}.txt"

    # 1. Captura de pantalla
    capturar_pantalla(nombre_img)

    # 2. Procesar imagen
    descripcion = extraer_texto(nombre_img)
    if descripcion:
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(descripcion)
        print(f"Descripción generada guardada en: {nombre_txt}")
    else:
        print("No se generó descripción de la imagen.")

    return nombre_img, nombre_txt