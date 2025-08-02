from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os

from selenium.webdriver.chrome.service import Service

def iniciar_driver():
    options = Options()
    options.add_argument("--start-maximized")

    driver_path = r"C:\Users\user\Desktop\VozAssistant\chromedriver-win64\chromedriver.exe"  # o ruta completa si no está en PATH
    service = Service(executable_path=driver_path)

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def buscar_producto(driver, termino):
    try:
        driver.get("https://www.mercadolibre.com.co")
        time.sleep(2)
        barra_busqueda = driver.find_element(By.NAME, "as_word")
        barra_busqueda.send_keys(termino)
        barra_busqueda.send_keys(Keys.ENTER)
        time.sleep(3)
        return f"Buscando producto: {termino}"
    except Exception as e:
        return f"Error al buscar producto: {e}"

def iniciar_sesion(driver):
    try:
        driver.get("https://www.mercadolibre.com.co")
        time.sleep(2)
        driver.find_element(By.LINK_TEXT, "Ingresa").click()
        time.sleep(2)
        return "Abriendo página de inicio de sesión."
    except Exception as e:
        return f"Error al intentar iniciar sesión: {e}"

def crear_cuenta(driver):
    try:
        driver.get("https://www.mercadolibre.com.co")
        time.sleep(2)
        driver.find_element(By.LINK_TEXT, "Crea tu cuenta").click()
        time.sleep(2)
        return "Abriendo página para crear cuenta."
    except Exception as e:
        return f"Error al crear cuenta: {e}"

def ejecutar_accion_externa(texto_usuario, driver):
    texto = texto_usuario.lower()

    if "buscar" in texto:
        termino = texto.split("buscar")[-1].strip()
        return buscar_producto(driver, termino)
    elif "iniciar sesión" in texto or "inicia sesión" in texto:
        return iniciar_sesion(driver)
    elif "crear cuenta" in texto or "registrarme" in texto:
        return crear_cuenta(driver)
    else:
        return "No entendí la acción a realizar en Mercado Libre."

if __name__ == "__main__":
    # Prueba rápida
    resultado = ejecutar_accion_externa("Buscar audífonos bluetooth")
    print(resultado)
