import requests
import os

OLLAMA_MODEL = "mistral:latest"  # Cambiar si se desea usar otro modelo
OLLAMA_HOST = "http://localhost:11434/api/generate"

def leer_archivo(path):
    if not path or not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def construir_prompt(transcripcion_path, inicio_path, final_path):
    transcripcion = leer_archivo(transcripcion_path)
    #descripcion_inicio = leer_archivo(inicio_path)
    descripcion_final = leer_archivo(final_path)

    prompt = f"""Actúa como un asistente virtual que observa la pantalla de un usuario y escucha su voz. 
A continuación tienes la transcripción de lo que el usuario dijo, seguido de la descripción de lo que se veía en pantalla antes y después de hablar.

TRANSCRIPCIÓN DE VOZ:
{transcripcion}

DESCRIPCIÓN DE PANTALLA FINAL:
{descripcion_final}

Responde la pregunta del usuario basándote en el contexto visual y su petición.
"""
    return prompt



#### VERSION NETAMENTE LOCAL CON MODELOS OLLAMA PARA PROCESADO DE CONSULTAS

def consultar_llm(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(OLLAMA_HOST, json=payload)
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        print(f"Error al consultar el modelo de lenguaje: {e}")
        return None

        

def procesar_interaccion(transcripcion_path, inicio_path, final_path):
    prompt = construir_prompt(transcripcion_path, inicio_path, final_path)
    respuesta = consultar_llm(prompt)
    if respuesta:
        print(f"\nRESPUESTA DEL ASISTENTE:\n{respuesta}\n")
        with open("respuesta.txt", "w", encoding="utf-8") as f:
            f.write(respuesta)
    else:
        print("No se obtuvo respuesta del modelo.")
