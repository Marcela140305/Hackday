import speech_recognition as sr
import pyttsx3
import unicodedata
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

CHROMEDRIVER_PATH = "C:/Users/SoporteTI/Documents/chromedriver-win64/chromedriver-win64/chromedriver.exe"

driver = None
acciones_clickables = []

PREGUNTAS_W = ["como", "que", "quien", "donde", "cuando", "por que", "porque"]
IGNORAR_CLICK_EN = ["click", "clic", "dale"]

def hablar(texto):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'spanish-latin-am')
    engine.say(texto)
    engine.runAndWait()

def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=6)
            try:
                texto = r.recognize_google(audio, language='es-CO')
                print(f"Has dicho (ES): {texto}")
                return texto.lower()
            except sr.UnknownValueError:
                pass
            try:
                texto = r.recognize_google(audio, language='en-US')
                print(f"Has dicho (EN): {texto}")
                return texto.lower()
            except sr.UnknownValueError:
                hablar("No entendí lo que dijiste, por favor repite.")
                return ""
        except sr.WaitTimeoutError:
            hablar("No escuché nada, por favor repite.")
            return ""
        except sr.RequestError:
            hablar("Hubo un error con el servicio de reconocimiento de voz.")
            return ""

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
    except Exception:
        hablar("Hubo un problema al escanear la página actual.")

def buscar_opciones_mas_cercanas(frase_usuario, acciones, umbral_similitud=0.6, max_resultados=5):
    frase_normalizada = frase_usuario.lower().strip()
    coincidencias = []
    for accion in acciones:
        texto_accion = accion["texto"].lower().strip()
        sim = similitud(frase_normalizada, texto_accion)
        if frase_normalizada in texto_accion or sim >= umbral_similitud:
            coincidencias.append((sim, accion))
    coincidencias.sort(key=lambda x: x[0], reverse=True)
    return [accion for _, accion in coincidencias[:max_resultados]]

def buscar_y_click(frase):
    global acciones_clickables, driver
    if not driver:
        hablar("Primero abre una página web antes de intentar hacer click.")
        return

    escanear_elementos_clickables()
    frase = limpiar_comando(frase)
    frase_norm = normalizar_texto(frase, mantener_pregunta=True)
    coincidencias = buscar_opciones_mas_cercanas(frase_norm, acciones_clickables)

    if not coincidencias:
        hablar(f"No encontré ninguna opción relacionada con {frase}.")
        return

    if len(coincidencias) == 1 or es_pregunta_w(frase):
        try:
            driver.execute_script("arguments[0].click();", coincidencias[0]["elemento"])
            hablar(f"He hecho click en {coincidencias[0]['original']}.")
            time.sleep(4)
            escanear_elementos_clickables()
            hablar("Estoy listo, espero tus órdenes.")
        except:
            hablar("No se pudo hacer click en el elemento.")
        return

    hablar(f"He encontrado {len(coincidencias)} opciones para {frase}.")
    for i, a in enumerate(coincidencias, 1):
        print(f"{i}. {a['original']}")
        hablar(f"Opción {i}: {a['original']}.")

    while True:
        hablar("Dime el número de la opción o di 'cancelar'.")
        eleccion = escuchar()
        if not eleccion:
            continue

        eleccion_norm = eleccion.strip().lower()
        if any(x in eleccion_norm for x in ["cancelar", "salir", "ninguna"]):
            hablar("Cancelando la selección.")
            return

        numeros = {
            "uno": 1, "una": 1, "opcion uno": 1, "opción uno": 1,
            "dos": 2, "opcion dos": 2, "opción dos": 2,
            "tres": 3, "opcion tres": 3, "opción tres": 3,
            "cuatro": 4, "opcion cuatro": 4, "opción cuatro": 4,
            "cinco": 5, "opcion cinco": 5, "opción cinco": 5
        }

        idx = None
        for palabra in eleccion_norm.split():
            if palabra.isdigit():
                idx = int(palabra)
                break
        if idx is None and eleccion_norm in numeros:
            idx = numeros[eleccion_norm]

        if idx and 1 <= idx <= len(coincidencias):
            try:
                driver.execute_script("arguments[0].click();", coincidencias[idx - 1]["elemento"])
                hablar(f"He hecho click en la opción {idx}: {coincidencias[idx - 1]['original']}.")
                time.sleep(4)
                escanear_elementos_clickables()
                hablar("Estoy listo, espero tus órdenes.")
            except:
                hablar("No se pudo hacer click en el elemento seleccionado.")
            return
        else:
            hablar("No entendí el número, intenta de nuevo.")

def abrir_pagina(palabra):
    global driver
    if not driver:
        opciones = Options()
        opciones.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opciones)
    driver.get("https://www.google.com")
    time.sleep(4)
    escanear_elementos_clickables()
    hablar("Estoy listo, espero tus órdenes.")

if __name__ == "__main__":
    hablar("Hola, soy ZOK. ¿En qué puedo ayudarte hoy?")
    while True:
        comando = escuchar()
        if comando:
            if "abrir" in comando and "google" in comando:
                abrir_pagina("google")
            elif "regresar" in comando or "atrás" in comando:
                if driver:
                    driver.back()
                    time.sleep(3)
                    escanear_elementos_clickables()
                    hablar("Estoy listo, espero tus órdenes.")
            elif any(x in comando for x in ["terminar", "salir", "adiós", "chao"]):
                hablar("De nada. ¡Hasta luego!")
                break
            else:
                buscar_y_click(comando)
