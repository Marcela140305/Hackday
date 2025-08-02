# modulo_externo/Modulo_Selenium.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import unicodedata
from difflib import SequenceMatcher
import os

CHROMEDRIVER_PATH = r"C:\Users\user\Desktop\VozAssistant\chromedriver-win64\chromedriver.exe"

driver = None
acciones_clickables = []

PREGUNTAS_W = ["como", "que", "quien", "donde", "cuando", "por que", "porque"]
IGNORAR_CLICK_EN = ["click", "clic", "dale"]

# ---------- Utilidades ----------
def normalizar_texto(texto, mantener_pregunta=False):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    if not mantener_pregunta:
        texto = texto.replace("\u00bf", "").replace("?", "")
    return texto.strip()

def limpiar_comando(frase):
    palabras = frase.split()
    resultado = [p for p in palabras if p not in IGNORAR_CLICK_EN]
    return ' '.join(resultado)

def similitud(a, b):
    return SequenceMatcher(None, a, b).ratio()

def es_pregunta_w(texto):
    texto = normalizar_texto(texto)
    return any(palabra in texto for palabra in PREGUNTAS_W)

# ---------- Acciones ----------
def abrir_pagina(url="https://www.google.com"):
    global driver
    if not driver:
        opciones = Options()
        opciones.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opciones)
    driver.get(url)
    time.sleep(3)
    escanear_elementos_clickables()

def escanear_elementos_clickables():
    global acciones_clickables, driver
    acciones_clickables = []
    if not driver:
        return
    try:
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        elementos = driver.find_elements(By.XPATH, "//a | //button | //*[@onclick] | //*[@role='button'] | //img[@alt]")
        vistos = set()
        for elem in elementos:
            try:
                if not elem.is_displayed():
                    continue
                texto_visible = (elem.text or "").strip()
                if not texto_visible:
                    texto_visible = driver.execute_script("return arguments[0].innerText || arguments[0].alt || ''", elem).strip()
                if texto_visible and len(texto_visible) > 2:
                    texto_norm = normalizar_texto(texto_visible, mantener_pregunta=True)
                    if texto_norm not in vistos:
                        acciones_clickables.append({
                            "texto": texto_norm,
                            "elemento": elem,
                            "original": texto_visible
                        })
                        vistos.add(texto_norm)
            except Exception:
                continue
    except Exception as e:
        print("Error al escanear la página:", e)

def buscar_opciones_mas_cercanas(frase_usuario, umbral_similitud=0.6, max_resultados=5):
    frase_normalizada = frase_usuario.lower().strip()
    coincidencias = []
    for accion in acciones_clickables:
        texto_accion = accion["texto"].lower().strip()
        sim = similitud(frase_normalizada, texto_accion)
        if frase_normalizada in texto_accion or sim >= umbral_similitud:
            coincidencias.append((sim, accion))
    coincidencias.sort(key=lambda x: x[0], reverse=True)
    return [accion for _, accion in coincidencias[:max_resultados]]

def ejecutar_click(frase):
    global driver
    if not driver:
        print("Primero abre una página web antes de hacer clic.")
        return "No hay navegador abierto."

    escanear_elementos_clickables()
    frase = limpiar_comando(frase)
    frase_norm = normalizar_texto(frase, mantener_pregunta=True)
    coincidencias = buscar_opciones_mas_cercanas(frase_norm)

    if not coincidencias:
        return f"No encontré ninguna opción relacionada con '{frase}'."

    try:
        driver.execute_script("arguments[0].click();", coincidencias[0]["elemento"])
        time.sleep(3)
        escanear_elementos_clickables()
        return f"He hecho clic en '{coincidencias[0]['original']}'."
    except:
        return "No se pudo hacer clic en el elemento."

def regresar_pagina():
    global driver
    if driver:
        driver.back()
        time.sleep(3)
        escanear_elementos_clickables()
        return "He regresado a la página anterior."
    return "No hay navegador activo."

def cerrar_navegador():
    global driver
    if driver:
        driver.quit()
        driver = None
        return "Navegador cerrado."
    return "No había navegador abierto."

def leer_peticion_guardada():
    ruta = "nuevapeticion.txt"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def ejecutar_accion_externa(mensaje):
    mensaje_norm = normalizar_texto(mensaje)
    
    if "abrir" in mensaje_norm and "pagina" in mensaje_norm:
        return abrir_pagina()

    if "cerrar" in mensaje_norm or "salir" in mensaje_norm:
        return cerrar_navegador()

    if "regresar" in mensaje_norm or "atras" in mensaje_norm:
        return regresar_pagina()

    if any(p in mensaje_norm for p in ["clic", "click", "dale", "presiona"]):
        return ejecutar_click(mensaje)

    return "No entendí qué acción deseas que realice en la página."


