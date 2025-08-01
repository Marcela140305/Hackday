import speech_recognition as sr
import pyttsx3
import unicodedata
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Ruta al ejecutable de ChromeDriver
CHROMEDRIVER_PATH = "C:/Users/SoporteTI/Documents/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# Variables globales para el navegador y elementos detectados
driver = None
acciones_clickables = []
campos_llenables = []

# Palabras que ayudan a entender preguntas o comandos irrelevantes en clics
PREGUNTAS_W = ["como", "que", "quien", "donde", "cuando", "por que", "porque"]
IGNORAR_CLICK_EN = ["click", "clic", "dale"]

# Hablar en voz alta utilizando pyttsx3
def hablar(texto):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'spanish-latin-am')
    engine.say(texto)
    engine.runAndWait()

# Escucha comandos del micrófono y retorna el texto en minúsculas
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

# Normaliza texto (quita tildes, minúsculas, signos)
def normalizar_texto(texto, mantener_pregunta=False):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    if not mantener_pregunta:
        texto = texto.replace("\u00bf", "").replace("?", "")
    return texto.strip()

# Elimina palabras como "clic", "dale", etc.
def limpiar_comando(frase):
    palabras = frase.split()
    resultado = [p for p in palabras if p not in IGNORAR_CLICK_EN]
    return ' '.join(resultado)

# Calcula similitud entre dos textos
def similitud(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Verifica si un texto parece una pregunta (para evitar confundir con opción clicable)
def es_pregunta_w(texto):
    texto = normalizar_texto(texto)
    return any(palabra in texto for palabra in PREGUNTAS_W)

# Escanea la página actual y detecta elementos clicables y campos
def escanear_elementos_clickables():
    global acciones_clickables, campos_llenables, driver
    acciones_clickables = []
    campos_llenables = []
    if not driver:
        return
    try:
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        elementos = driver.find_elements(By.XPATH, "//a | //button | //*[@onclick] | //*[@role='button'] | //img[@alt]")
        inputs = driver.find_elements(By.XPATH, "//input | //textarea")

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

        for campo in inputs:
            try:
                label = campo.get_attribute("aria-label") or campo.get_attribute("placeholder") or campo.get_attribute("name")
                if not label:
                    label = driver.execute_script("return arguments[0].labels && arguments[0].labels[0] ? arguments[0].labels[0].innerText : ''", campo)
                if label:
                    campos_llenables.append({
                        "texto": normalizar_texto(label),
                        "original": label,
                        "elemento": campo
                    })
            except Exception:
                continue
    except Exception:
        hablar("Hubo un problema al escanear la página actual.")

# Convierte frases habladas como "arroba", "punto" y quita espacios en contraseñas
def procesar_valor(valor, campo_texto):
    valor = valor.replace(" arroa ", "@").replace(" arroba ", "@").replace(" punto ", ".")
    valor = valor.replace(" ", "") if "contrasena" in campo_texto or "password" in campo_texto else valor
    return valor.strip()

# Maneja la lógica de borrar o corregir un campo
def borrar_o_corrigir_campo(comando):
    global campos_llenables
    escanear_elementos_clickables()
    accion = "borrar" if "borr" in comando else "corregir"
    patron = re.search(rf"{accion}\s+(?:el\s+)?(?:campo\s+)?(?:de\s+)?(.*?)\s*(?:con\s+(.*))?", comando)
    if not patron:
        hablar("No entendí qué campo quieres modificar.")
        return
    campo_texto = normalizar_texto(patron.group(1))
    nuevo_valor = patron.group(2) if accion == "corregir" else None
    coincidencias = buscar_opciones_mas_cercanas(campo_texto, campos_llenables)
    if not coincidencias:
        hablar(f"No encontré el campo {campo_texto}.")
        return
    campo = coincidencias[0]["elemento"]
    campo.clear()
    if accion == "corregir" and nuevo_valor:
        nuevo_valor = procesar_valor(nuevo_valor, campo_texto)
        campo.send_keys(nuevo_valor)
        hablar(f"He corregido el campo {coincidencias[0]['original']} con {nuevo_valor}.")
    else:
        hablar(f"He borrado el contenido del campo {coincidencias[0]['original']}.")

# Llena un campo con el valor dictado
def llenar_campo_por_voz(comando):
    global campos_llenables
    patron = re.search(r"llen(a|ar)?(?:\s+el)?(?:\s+campo)?(?:\s+de)?\s+(.*?)\s+con\s+(.*)", comando)
    if not patron:
        hablar("No entendí el campo que deseas llenar.")
        return

    campo_texto = normalizar_texto(patron.group(2))
    valor = patron.group(3).strip()
    valor_procesado = procesar_valor(valor, campo_texto)

    coincidencias = buscar_opciones_mas_cercanas(campo_texto, campos_llenables)

    if coincidencias:
        campo = coincidencias[0]["elemento"]
        campo.clear()
        campo.send_keys(valor_procesado)
        if not ("contrasena" in campo_texto or "password" in campo_texto):
            hablar(f"He llenado el campo de {coincidencias[0]['original']} con {valor_procesado}.")
    else:
        hablar(f"No encontré un campo relacionado con {campo_texto}.")

# Busca opciones similares a lo dicho y ordena por similitud
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

# Busca y hace clic en elementos, o pregunta por opciones si hay varias
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
            hablar("Estoy lista, esperando órdenes.")
        except:
            hablar("No se pudo hacer click en el elemento.")
        return

    hablar(f"He encontrado {len(coincidencias)} opciones para {frase}.")
    for i, a in enumerate(coincidencias, 1):
        print(f"{i}. {a['original']}")
        hablar(f"Opción {i}: {a['original']}.")

    hablar("Dime el número de la opción o di 'cancelar'.")

    while True:
        eleccion = escuchar()
        if not eleccion:
            continue
        if any(palabra in eleccion for palabra in ["cancelar", "salir", "ninguna"]):
            hablar("Cancelando la selección.")
            return

        numeros = {"uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
        idx = None
        for palabra in eleccion.split():
            if palabra.isdigit():
                idx = int(palabra)
                break
            if palabra in numeros:
                idx = numeros[palabra]
                break

        if idx and 1 <= idx <= len(coincidencias):
            try:
                driver.execute_script("arguments[0].click();", coincidencias[idx - 1]["elemento"])
                hablar(f"He hecho click en la opción {idx}: {coincidencias[idx - 1]['original']}.")
                time.sleep(4)
                escanear_elementos_clickables()
                hablar("Estoy lista, esperando órdenes.")
            except:
                hablar("No se pudo hacer click en el elemento seleccionado.")
            return
        else:
            hablar("No entendí el número, intenta de nuevo.")

# Abre el navegador en una URL inicial y escanea automáticamente
def abrir_pagina(palabra):
    global driver
    if not driver:
        opciones = Options()
        opciones.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opciones)
    driver.get("https://www.google.com")
    time.sleep(4)
    escanear_elementos_clickables()
    hablar("Estoy lista, esperando órdenes.")

# Bucle principal del asistente
def main():
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
                    hablar("Estoy lista, esperando órdenes.")
            elif any(x in comando for x in ["terminar", "salir", "adiós", "chao"]):
                hablar("De nada. ¡Hasta luego!")
                break
            elif "borrar" in comando or "corrige" in comando or "corregir" in comando:
                borrar_o_corrigir_campo(comando)
            elif "llenar" in comando or "llena" in comando:
                llenar_campo_por_voz(comando)
            else:
                buscar_y_click(comando)

# Punto de entrada principal del asistente de voz.
# Este bloque se ejecuta solo si el archivo se ejecuta directamente (no si se importa como módulo).
if __name__ == "__main__":
    hablar("Hola, soy ZOK. ¿En qué puedo ayudarte hoy?")
    while True:
        comando = escuchar()  # Espera entrada de voz del usuario
        if comando:
            # Comando para abrir Google
            if "abrir" in comando and "google" in comando:
                abrir_pagina("google")
            # Comando para retroceder en el navegador
            elif "regresar" in comando or "atrás" in comando:
                if driver:
                    driver.back()
                    time.sleep(3)
                    escanear_elementos_clickables()
                    hablar("Estoy lista, esperando órdenes.")
            # Comando para salir o finalizar sesión
            elif any(x in comando for x in ["terminar", "salir", "adiós", "chao"]):
                hablar("De nada. ¡Hasta luego!")
                break
            # Comando para borrar o corregir campos de formularios
            elif "borrar" in comando or "corrige" in comando or "corregir" in comando:
                borrar_o_corrigir_campo(comando)
            # Comando para llenar campos con voz
            elif "llenar" in comando or "llena" in comando:
                llenar_campo_por_voz(comando)
            # Por defecto, intenta buscar y hacer clic en algún elemento
            else:
                buscar_y_click(comando)

