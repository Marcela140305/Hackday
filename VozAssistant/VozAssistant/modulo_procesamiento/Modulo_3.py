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

RECOMENDACIÓN FINAL PARA RESPUESTAS:
1) Se conciso en tus respuestas basado en el contexto que se te da y no des tanto detalle si no es explicitamente solicitado
2) Ten en cuenta que si la petición del usuario solicita autocompletar formularios o inicios de sesión, debes indicar que no tienes la autorización para manejar datos personales pero que puedes indicarle que campos debe llenar segun lo que se visualiza en pantalla.
# Esto solo debes decirlo en caso que la petición sea completar o llenar un formulario o inicio de sesión. En las demas consultas no debes mencionar esta restricción.
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
