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
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    driver_path = r"C:\Users\user\Desktop\VozAssistant\chromedriver-win64\chromedriver.exe"  # o ruta completa si no está en PATH
    service = Service(executable_path=driver_path)

    driver = webdriver.Chrome(service=service, options=options)
    # Cargar Google en la pestaña inicial
    driver.get("https://www.mercadolibre.com.co")
    time.sleep(2)  # Espera leve para que cargue antes de más acciones

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
    

def click_enlace_por_texto(driver, texto_visible):
    try:
        boton = driver.find_element(By.XPATH, f"//a[contains(text(), '{texto_visible}')]")
        boton.click()
        return f"Se ha ingresado a la sección: {texto_visible}"
    except Exception as e:
        return f"No se pudo acceder a {texto_visible}: {e}"


def ejecutar_accion_externa(texto_usuario, driver):
    texto = texto_usuario.lower()

    if "buscar" in texto:
        termino = texto.split("buscar")[-1].strip()
        return buscar_producto(driver, termino)
    elif "iniciar sesión" in texto or "inicia sesión" in texto:
        return iniciar_sesion(driver)
    elif "crear cuenta" in texto or "registrarme" in texto:
        return crear_cuenta(driver)
    elif "carrito" in texto:
        return click_enlace_por_texto(driver, "Carrito")
    elif "mis compras" in texto or "mis órdenes" in texto:
        return click_enlace_por_texto(driver, "Mis compras")
    elif "ofertas" in texto:
        return click_enlace_por_texto(driver, "Ofertas")
    elif "cupones" in texto:
        return click_enlace_por_texto(driver, "Cupones")
    elif "supermercado" in texto:
        return click_enlace_por_texto(driver, "Supermercado")
    elif "moda" in texto:
        return click_enlace_por_texto(driver, "Moda")
    elif "vender" in texto:
        return click_enlace_por_texto(driver, "Vender")
    elif "ayuda" in texto or "pqr" in texto:
        return click_enlace_por_texto(driver, "Ayuda")
    else:
        return "No entendí la acción a realizar en Mercado Libre."

if __name__ == "__main__":
    # Prueba rápida
    resultado = ejecutar_accion_externa("Buscar audífonos bluetooth")
    print(resultado)
